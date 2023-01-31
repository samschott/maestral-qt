# -*- coding: utf-8 -*-

# system imports
import os
import threading
from queue import Queue

# external packages
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtCore import pyqtSignal as Signal

# maestral modules
from maestral.daemon import MaestralProxy
from maestral.exceptions import NotAFolderError, NotFoundError, BusyError
from maestral.utils.path import is_child, is_equal_or_child
from maestral.core import FolderMetadata

# local imports
from .utils import BackgroundTask
from .widgets import UserDialog
from .resources import native_folder_icon, native_file_icon
from .resources.ui_selective_sync_dialog import Ui_SelectiveSyncDialog


# noinspection PyTypeChecker
class FileSystemModel(QAbstractItemModel):
    """A QAbstractItemModel which loads items and their children on-demand and
    asynchronously. It is useful for displaying a hierarchy from a source which is
    slow to load (remote server, slow file system, etc)."""

    loading_failed = Signal()
    loading_done = Signal()

    def __init__(self, root, parent=None, checkbox_column=1):
        super().__init__(parent=parent)
        self._root_item = root
        self._root_item.loading_done.connect(self.reloadData)
        self._root_item.loading_failed.connect(self.on_loading_failed)
        self._header = self._root_item.header()
        self._flags = Qt.ItemFlag.ItemIsUserCheckable
        self.checkbox_column = checkbox_column

    def on_loading_failed(self):
        self.display_message(
            "Could not connect to Dropbox. Please check your internet connection."
        )

    def display_message(self, message):
        self._root_item._children = [MessageTreeItem(self._root_item, message=message)]

        self.loading_failed.emit()
        self.modelReset.emit()

    def reloadData(self, roles=None):
        if not roles:
            roles = [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.CheckStateRole]

        self.dataChanged.emit(QModelIndex(), QModelIndex(), roles)
        self.layoutChanged.emit()
        self.loading_done.emit()

    def flags(self, index):
        flags = super().flags(index) | self._flags
        return flags

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().column_count()
        else:
            return len(self._header)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()
        return parent_item.child_count()

    def hasChildren(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().can_have_children
        else:
            return True

    def checkState(self, index):
        if not index.isValid():
            return None
        else:
            return index.internalPointer().checkState

    def setCheckState(self, index, value):
        if index.isValid():
            item = index.internalPointer()
            item.checkState = value
            self.dataChanged.emit(index, index)
            self.layoutChanged.emit()
            return True
        return False

    def setData(self, index, value, role):
        if (
            role == Qt.ItemDataRole.CheckStateRole
            and index.column() == self.checkbox_column
        ):
            self.setCheckState(index, value)
            return True

        return super().setData(index, value, role)

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return item.data(column)
        if role == Qt.ItemDataRole.CheckStateRole and column == self.checkbox_column:
            return item.checkState
        if role == Qt.ItemDataRole.DecorationRole and column == 0:
            return item.icon
        return None

    def headerData(self, column, orientation, role):
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            try:
                return self._header[column]
            except IndexError:
                pass
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item = parent.internalPointer()
        child_item = parent_item.child_at(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        child_item = index.internalPointer()
        if not child_item:
            return QModelIndex()
        parent_item = child_item.parent_()
        if parent_item == self._root_item:
            return QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        self._root_item.sort(column, order)
        self.dataChanged.emit(QModelIndex(), QModelIndex())
        self.layoutChanged.emit()


class AbstractTreeItem(QtCore.QObject):
    """
    An abstract item for `TreeModel`. To be subclassed depending on the application.
    """

    loading_done = Signal()
    loading_failed = Signal()

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent=parent)
        self._children = []
        self._parent = parent
        self._children_update_started = False
        self._children_update_completed = False
        self._checkStateChanged = False

        if self._parent:
            self.loading_done.connect(self._parent.loading_done)
            self.loading_failed.connect(self._parent.loading_failed)

        self.icon = QtGui.QIcon()
        self._checkState = 0
        self.can_have_children = True

    @property
    def checkState(self):
        return self._checkState

    @checkState.setter
    def checkState(self, state):
        self._checkStateChanged = True
        self._checkState = state

        self._checkStatePropagateToChildren(state)
        self._checkStatePropagateToParent(state)

    def _checkStatePropagateToChildren(self, state):
        pass

    def _checkStatePropagateToParent(self, state):
        pass

    def header(self):
        # subclass this
        raise NotImplementedError(self.header)

    def column_count(self):
        return len(self.header())

    def parent_(self):
        return self._parent

    def _async_loading_done(self, result):
        raise NotImplementedError(self._async_loading_done)

    def _create_children_async(self):
        raise NotImplementedError(self._create_children_async)

    def row(self):
        if self._parent:
            return self._parent._children.index(self)
        return 0

    def children_(self):
        if not self._children_update_started:
            self._create_children_async()
            self._children_update_started = True
        return self._children

    def child_at(self, row):
        return self.children_()[row]

    def data(self, column):
        # subclass this
        raise NotImplementedError(self.data)

    def child_count(self):
        """The number of children. Calling this method will trigger loading."""
        return len(self.children_())

    def child_count_loaded(self):
        """The number of children already loaded."""
        return len(self._children) if self._children_update_started else 0

    def isSelectionModified(self):
        return False

    def sort(self, column, order):
        pass


class MessageTreeItem(AbstractTreeItem):
    """A tree item to display a message instead of contents."""

    def __init__(self, parent=None, message=""):
        AbstractTreeItem.__init__(self, parent=parent)
        self._parent = parent
        self._message = message
        self._checkState = None
        self.can_have_children = False

    def _async_loading_done(self, result):
        pass

    def _create_children_async(self):
        pass

    def child_at(self, row):
        return None

    def data(self, column):
        return (self._message, "")[column]

    def header(self):
        return ["Name", "Included"]


def _sort_key(item, column, reverse):
    if column == 0 and isinstance(item, DropboxPathItem):
        if item.is_folder is not reverse:
            prefix = "\x00"
        else:
            prefix = ""

        return f"{prefix}{item._basename.lower()}"

    elif column == 1:
        return item.checkState
    else:
        return item.data(column)


class DropboxPathItem(AbstractTreeItem):
    """A Dropbox folder item. It lists its children asynchronously, only when asked to
    by `TreeModel`."""

    def __init__(
        self,
        async_loader,
        unchecked,
        path_display="/",
        path_lower="/",
        is_folder=True,
        parent=None,
    ):
        super().__init__(parent=parent)
        if is_folder:
            self.icon = native_folder_icon()
            self._children = [MessageTreeItem(self, "Loading...")]
        else:
            self.icon = native_file_icon()
            self._children = []
        self.is_folder = is_folder
        self.can_have_children = is_folder
        self._path_display = path_display
        self._path_lower = path_lower
        self._basename = os.path.basename(self._path_display)
        self._async_loader = async_loader
        self._unchecked = unchecked

        self._checkStateChanged = False

        # get info from our own excluded list
        if path_lower in unchecked:
            # item is excluded
            self._originalCheckState = 0
        elif self._parent is not None and self._parent._originalCheckState == 0:
            # item's parent is excluded
            self._originalCheckState = 0
        elif any(is_child(f, path_lower) for f in unchecked):
            # some of item's children are excluded
            self._originalCheckState = 1
        else:
            # item is fully included
            self._originalCheckState = 2

        # overwrite original state if the parent was modified
        if (
            self._parent is not None
            and self._parent._checkStateChanged
            and not self._parent.checkState == 1
        ):
            # inherit from parent
            self._checkState = self._parent.checkState
            self._checkStateChanged = self._parent._checkStateChanged
        else:
            self._checkStateChanged = False
            self._checkState = int(self._originalCheckState)

    def _create_children_async(self):
        if self.is_folder:
            self._remote = self._async_loader.listChildren(self._path_lower)
            self._remote.sig_result.connect(self._async_loading_done)
        else:
            self._async_loading_done([])

    def _async_loading_done(self, results):
        if isinstance(results, Exception):
            raise results

        for child in self._children.copy():
            if isinstance(child, MessageTreeItem):
                self._children.remove(child)

        if results is False:
            self.loading_failed.emit()
        else:
            new_nodes = [
                DropboxPathItem(
                    self._async_loader,
                    self._unchecked,
                    path_display=e.path_display,
                    path_lower=e.path_lower,
                    is_folder=isinstance(e, FolderMetadata),
                    parent=self,
                )
                for e in results
            ]
            self._children.extend(new_nodes)
            self.sort(0, Qt.SortOrder.AscendingOrder)
            self.loading_done.emit()

    def data(self, column):
        return (self._basename, "")[column]

    def header(self):
        return ["Name", "Included"]

    def _checkStatePropagateToChildren(self, state):
        # propagate to children if checked or unchecked
        if state in (0, 2) and self.child_count_loaded() > 0:
            for child in self._children:
                child._checkStateChanged = True
                child._checkState = state
                child._checkStatePropagateToChildren(state)

    def _checkStatePropagateToParent(self, state):
        # propagate to parent if checked or unchecked
        if self._parent:
            self._parent._checkStateChanged = True
            # get minimum of all other children's check state
            checkstate_other_children = min(
                c.checkState for c in self._parent._children
            )
            # set parent's state to that minimum, if it >= 1 (there always could be
            # included files)
            new_parent_state = max([checkstate_other_children, 1])
            self._parent._checkState = new_parent_state
            # tell the parent to propagate its own state upwards
            self._parent._checkStatePropagateToParent(state)

    @property
    def checkStateChanged(self):
        return self._checkStateChanged

    def isSelectionModified(self):
        own_selection_modified = self._checkState != self._originalCheckState
        child_selection_modified = any(c.isSelectionModified() for c in self._children)
        return own_selection_modified or child_selection_modified

    def sort(self, column, order):
        reverse = order == Qt.SortOrder.DescendingOrder

        self._children.sort(
            key=lambda x: _sort_key(x, column, reverse), reverse=reverse
        )

        for child in self._children:
            child.sort(column, order)


class AsyncListFolder(QtCore.QObject):
    def __init__(self, config_name, parent=None):
        """
        A helper which creates instances of :class:`BackgroundTask` to
        asynchronously list Dropbox folders

        :param str config_name: Config name of Maestral instance
        :param parent: QObject. Defaults to None.
        """
        super().__init__(parent=parent)
        self.config_name = config_name
        self._abort_event = threading.Event()

    def abortListing(self):
        self._abort_event.set()

    def listChildren(self, path):
        """
        Returns a running instance of :class:`maestral.gui.utils.BackgroundTask` which
        will emit `sig_result` once it has a result.
        :param str path: Dropbox path to list.
        :returns: Running background task.
        :rtype: :class:`maestral.gui.utils.BackgroundTask`
        """

        new_job = BackgroundTask(parent=self, target=self._listChildren, args=(path,))

        return new_job

    def _listChildren(self, path):
        """The actual function which does the listing. Returns an iterator over the
        entries in the Dropbox folder."""

        # use a duplicate proxy to prevent blocking of the main connection
        with MaestralProxy(self.config_name) as m:
            entries_iterator = m.list_folder_iterator(path)

            while not self._abort_event.is_set():
                try:
                    entries = next(entries_iterator)
                    entries.sort(key=lambda e: e.name.lower())
                except (NotAFolderError, NotFoundError):
                    entries = []
                except ConnectionError:
                    entries = False
                except StopIteration:
                    return

                yield entries


# noinspection PyArgumentList
class SelectiveSyncDialog(QtWidgets.QDialog, Ui_SelectiveSyncDialog):
    def __init__(self, mdbx, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setModal(True)

        self.mdbx = mdbx
        self.dbx_model = None
        self.updateButton.setEnabled(False)

        self.ui_failed()

        # connect callbacks
        self.updateButton.clicked.connect(self.on_accepted)
        self.cancelButton.clicked.connect(self.close)
        self.selectAllCheckBox.clicked.connect(self.on_select_all_clicked)

    def populate_folders_list(self, overload=None):
        self.excluded_items = set(self.mdbx.excluded_items)
        self.async_loader = AsyncListFolder(self.mdbx.config_name, self)
        self.dbx_root = DropboxPathItem(
            async_loader=self.async_loader,
            unchecked=set(self.mdbx.excluded_items),
        )
        self.dbx_model = FileSystemModel(self.dbx_root)
        self.dbx_model.loading_done.connect(self.ui_loaded)
        self.dbx_model.loading_failed.connect(self.ui_failed)
        self.dbx_model.dataChanged.connect(self.update_select_all_checkbox)
        self.dbx_model.dataChanged.connect(self.update_dialog_buttons)
        self.treeViewFolders.setModel(self.dbx_model)

    def update_select_all_checkbox(self):
        check_states = []
        for irow in range(self.dbx_model._root_item.child_count_loaded()):
            index = self.dbx_model.index(irow, 1, QModelIndex())
            check_states.append(
                self.dbx_model.data(index, Qt.ItemDataRole.CheckStateRole)
            )

        if all(cs == 2 for cs in check_states):
            self.selectAllCheckBox.setChecked(True)
        else:
            self.selectAllCheckBox.setChecked(False)

    def update_dialog_buttons(self):
        self.updateButton.setEnabled(self.dbx_root.isSelectionModified())

    def on_select_all_clicked(self, checked):
        checked_state = 2 if checked else 0
        for irow in range(self.dbx_model._root_item.child_count_loaded()):
            index = self.dbx_model.index(irow, 1, QModelIndex())
            self.dbx_model.setCheckState(index, checked_state)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.async_loader.abortListing()

    def on_accepted(self, overload=None):
        """
        Apply changes to local Dropbox folder.
        """
        if not self.mdbx.connected:
            self.dbx_model.on_loading_failed()

        else:
            excluded_items = self.get_excluded_items()
            try:
                self.mdbx.excluded_items = excluded_items
            except BusyError as err:
                msg_box = UserDialog(err.title, err.message, parent=self)
                msg_box.open()
            else:
                self.accept()

    def get_excluded_items(self):
        # We load the old excluded list first. This is to preserve any exclusions of
        # sub-folders which may not be loaded in the GUI. We then update the excluded
        # list to reflect any changes made by the user in the GUI.
        excluded_items = set(self.mdbx.excluded_items)

        queue = Queue()
        queue.put(self.dbx_model._root_item)

        while not queue.empty():
            node = queue.get()

            # Include items which have been checked / partially checked.
            # Remove items which have been unchecked.
            # The list will be cleaned up later.

            if node.checkState == 0:
                # Path is fully excluded. Add to excluded list.
                excluded_items.add(node._path_lower)
            elif node.checkState == 1:
                # Path is included but has excluded children. Remove only the path
                # itself from the excluded list.
                excluded_items.discard(node._path_lower)
            elif node.checkState == 2:
                # Path is fully included. Remove it and all its children
                # from excluded list. We do this here because children might not
                # have been loaded / expanded and won't be visited during traversal.
                for path in excluded_items.copy():
                    if is_equal_or_child(path, node._path_lower):
                        excluded_items.discard(path)

            for child in node._children:
                if isinstance(child, DropboxPathItem):
                    queue.put(child)

        return excluded_items

    def ui_failed(self):
        self.updateButton.setEnabled(False)
        self.selectAllCheckBox.setEnabled(False)

    def ui_loaded(self):
        self.selectAllCheckBox.setEnabled(True)
        self.treeViewFolders.resizeColumnToContents(0)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.PaletteChange:
            self.update_dark_mode()

    def update_dark_mode(self):
        if self.dbx_model:
            self.dbx_model.reloadData(
                [Qt.ItemDataRole.DecorationRole]
            )  # reload folder icons

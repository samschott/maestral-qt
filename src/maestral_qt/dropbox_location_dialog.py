# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:23:13 2018

@author: samschott
"""

# system imports
import os.path as osp

# external imports
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtCore import Qt

# maestral modules
from maestral.utils.appdirs import get_home_dir
from maestral.utils.path import delete
from maestral.daemon import stop_maestral_daemon_process

# local imports
from .resources import APP_ICON_PATH, native_folder_icon
from .resources.ui_dropbox_location_dialog import Ui_Dialog
from .utils import MaestralBackgroundTask, icon_to_pixmap, is_empty
from .widgets import UserDialog


# noinspection PyArgumentList
class DropboxLocationDialog(QtWidgets.QDialog, Ui_Dialog):
    """A dialog to link and set up a new Dropbox account."""

    accepted = False

    def __init__(self, mdbx, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        # noinspection PyTypeChecker
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Sheet
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.CustomizeWindowHint
        )

        self.mdbx = mdbx
        self.config_name = self.mdbx.config_name

        self.app_icon = QtGui.QIcon(APP_ICON_PATH)

        self.labelIcon.setPixmap(icon_to_pixmap(self.app_icon, 60))

        # set up Dropbox location combobox

        self.dropbox_location = self.mdbx.get_conf("sync", "path")

        if self.dropbox_location == "":
            folder_name = f"Dropbox ({self.config_name.capitalize()})"
            self.dropbox_location = osp.join(get_home_dir(), folder_name)

        self.comboBoxPath.addItem(native_folder_icon(), self.dropbox_location)
        self.comboBoxPath.insertSeparator(1)
        self.comboBoxPath.addItem(QtGui.QIcon(), "Choose...")
        self.comboBoxPath.currentIndexChanged.connect(self.on_combobox)

        self.dropbox_folder_dialog = QtWidgets.QFileDialog(self)
        self.dropbox_folder_dialog.setAcceptMode(
            QtWidgets.QFileDialog.AcceptMode.AcceptOpen
        )
        self.dropbox_folder_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        self.dropbox_folder_dialog.setOption(
            QtWidgets.QFileDialog.Option.ShowDirsOnly, True
        )
        self.dropbox_folder_dialog.setLabelText(
            QtWidgets.QFileDialog.DialogLabel.Accept, "Select"
        )
        self.dropbox_folder_dialog.setDirectory(get_home_dir())
        self.dropbox_folder_dialog.fileSelected.connect(self.on_new_dbx_folder)
        self.dropbox_folder_dialog.rejected.connect(
            lambda: self.comboBoxPath.setCurrentIndex(0)
        )

        self.pushButtonSelect.setDefault(True)

        # connect buttons to callbacks
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.pushButtonQuit.clicked.connect(self.on_quit_clicked)
        self.pushButtonSelect.clicked.connect(self.on_selected_clicked)
        self.pushButtonUnlink.clicked.connect(self.on_unlink_clicked)

    # =============================================================================
    # Main callbacks
    # =============================================================================

    @QtCore.pyqtSlot()
    def on_quit_clicked(self):
        self._deactivate_buttons()
        self.spinner.startAnimation()
        stop_maestral_daemon_process(self.mdbx.config_name)

    @QtCore.pyqtSlot()
    def on_unlink_clicked(self):
        self._deactivate_buttons()
        self.spinner.startAnimation()

        self.unlink_task = MaestralBackgroundTask(
            parent=self,
            config_name=self.mdbx.config_name,
            target="unlink",
        )

        self.unlink_task.sig_result.connect(self.on_unlink_done)

    @QtCore.pyqtSlot()
    def on_unlink_done(self):
        self.spinner.stopAnimation()
        stop_maestral_daemon_process(self.mdbx.config_name)

    @QtCore.pyqtSlot()
    def on_selected_clicked(self):
        # apply dropbox path
        try:
            if osp.exists(self.dropbox_location):
                if is_empty(self.dropbox_location):
                    delete(self.dropbox_location, raise_error=True)
                else:
                    msg_box = UserDialog(
                        title="Folder is not empty",
                        message=(
                            f'The folder "{osp.basename(self.dropbox_location)}" is '
                            "not empty. Would you like to merge its content with your "
                            "Dropbox?"
                        ),
                        button_names=("Cancel", "Merge"),
                        parent=self,
                    )
                    res = msg_box.exec()

                    if res == UserDialog.DialogCode.Accepted:
                        return
                    elif res == UserDialog.DialogCode.Rejected:
                        pass

            self.mdbx.create_dropbox_directory(self.dropbox_location)
        except OSError:
            msg_box = UserDialog(
                title="Could not set directory",
                message=(
                    "Please check if you have permissions to write to the "
                    "selected location."
                ),
                parent=self,
            )
            msg_box.exec()
            return

        # Resume sync with clean sync state.
        self.mdbx.reset_sync_state()
        self.mdbx.start_sync()
        self.close()

    # =============================================================================
    # Helper functions
    # =============================================================================

    def _deactivate_buttons(self):
        self.pushButtonQuit.setEnabled(False)
        self.pushButtonSelect.setEnabled(False)
        self.pushButtonUnlink.setEnabled(False)
        self.comboBoxPath.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_combobox(self, idx):
        if idx == 2:
            self.dropbox_folder_dialog.open()

    @QtCore.pyqtSlot(str)
    def on_new_dbx_folder(self, new_location):
        self.comboBoxPath.setCurrentIndex(0)
        if not new_location == "":
            self.comboBoxPath.setItemText(0, new_location)

        self.dropbox_location = new_location

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.PaletteChange:
            self.update_dark_mode()

    def update_dark_mode(self):
        if self.dbx_model:
            # reload folder icons
            self.dbx_model.reloadData([Qt.ItemDataRole.DecorationRole])

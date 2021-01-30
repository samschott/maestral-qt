# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:23:13 2018

@author: samschott
"""
# system imports
import os.path as osp
import time
from distutils.version import LooseVersion

# external packages
from PyQt5 import QtGui, QtCore, QtWidgets, uic

# maestral modules
from maestral import __version__ as __daemon_version__
from maestral.utils.appdirs import get_home_dir

# local imports
from . import __version__, __author__, __url__
from .selective_sync_dialog import SelectiveSyncDialog
from .resources import (
    native_item_icon,
    UNLINK_DIALOG_PATH,
    SETTINGS_WINDOW_PATH,
    APP_ICON_PATH,
    FACEHOLDER_PATH,
)
from .utils import (
    IS_MACOS,
    LINE_COLOR_DARK,
    LINE_COLOR_LIGHT,
    get_scaled_font,
    is_dark_window,
    center_window,
    icon_to_pixmap,
    get_masked_image,
    MaestralBackgroundTask,
)
from .widgets import UserDialog
from .autostart import AutoStart

NEW_QT = LooseVersion(QtCore.QT_VERSION_STR) >= LooseVersion("5.11")


class UnlinkDialog(QtWidgets.QDialog):

    # noinspection PyArgumentList
    def __init__(self, mdbx, restart_func, parent=None):
        super().__init__(parent=parent)
        # load user interface layout from .ui file
        uic.loadUi(UNLINK_DIALOG_PATH, self)

        self.setWindowFlags(QtCore.Qt.Sheet)
        self.setModal(True)

        self.restart_func = restart_func
        self.mdbx = mdbx

        self.buttonBox.buttons()[0].setText("Unlink")
        self.titleLabel.setFont(get_scaled_font(bold=True))
        self.infoLabel.setFont(get_scaled_font(scaling=0.9))

        icon = QtGui.QIcon(APP_ICON_PATH)
        pixmap = icon_to_pixmap(icon, self.iconLabel.width(), self.iconLabel.height())
        self.iconLabel.setPixmap(pixmap)

    def accept(self):

        self.buttonBox.setEnabled(False)
        self.progressIndicator.startAnimation()
        self.unlink_thread = MaestralBackgroundTask(
            self, self.mdbx.config_name, "unlink"
        )
        self.unlink_thread.sig_result.connect(self.restart_func)


# noinspection PyArgumentList
class SettingsWindow(QtWidgets.QWidget):
    """A widget showing all of Maestral's settings."""

    _update_interval_mapping = {
        0: 60 * 60 * 24,
        1: 60 * 60 * 24 * 7,
        2: 60 * 60 * 24 * 30,
        3: 0,
    }

    def __init__(self, parent, mdbx):
        super().__init__()
        uic.loadUi(SETTINGS_WINDOW_PATH, self)

        if IS_MACOS:
            # noinspection PyTypeChecker
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self._parent = parent
        self.update_dark_mode()

        self.adjustSize()

        self.mdbx = mdbx
        self.selective_sync_dialog = SelectiveSyncDialog(self.mdbx, parent=self)
        self.unlink_dialog = UnlinkDialog(self.mdbx, self._parent.restart, parent=self)
        self.autostart = AutoStart(self.mdbx.config_name)
        self.default_dirname = f"Dropbox ({self.mdbx.config_name.capitalize()})"

        self.labelAccountName.setFont(get_scaled_font(1.5))
        self.labelAccountInfo.setFont(get_scaled_font(0.9))
        self.labelSpaceUsage.setFont(get_scaled_font(0.9))

        # fixes sizes of label and profile pic
        self.labelAccountName.setFixedHeight(self.labelAccountName.height())
        self._profile_pic_height = round(self.labelUserProfilePic.height() * 0.65)

        self.refresh_gui()

        # update profile pic and account info periodically
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.refresh_gui)
        self.update_timer.start(5000)  # every 5 sec

        # connect callbacks
        self.pushButtonUnlink.clicked.connect(self.unlink_dialog.exec_)
        self.pushButtonExcludedFolders.clicked.connect(
            self.selective_sync_dialog.populate_folders_list
        )
        self.pushButtonExcludedFolders.clicked.connect(self.selective_sync_dialog.open)
        self.checkBoxStartup.stateChanged.connect(self.on_start_on_login_clicked)
        self.checkBoxNotifications.stateChanged.connect(self.on_notifications_clicked)
        self.comboBoxUpdateInterval.currentIndexChanged.connect(
            self.on_combobox_update_interval
        )
        self.comboBoxDropboxPath.currentIndexChanged.connect(self.on_combobox_path)
        msg = (
            "Choose a location for your Dropbox. A folder named "
            f'"{self.default_dirname}" will be created inside the selected location.'
        )
        self.dropbox_folder_dialog = QtWidgets.QFileDialog(self, caption=msg)
        self.dropbox_folder_dialog.setModal(True)
        self.dropbox_folder_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        self.dropbox_folder_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        self.dropbox_folder_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        self.dropbox_folder_dialog.fileSelected.connect(self.on_new_dbx_folder)
        self.dropbox_folder_dialog.rejected.connect(
            lambda: self.comboBoxDropboxPath.setCurrentIndex(0)
        )

        center_window(self)

    @QtCore.pyqtSlot()
    def refresh_gui(self):

        # populate account info
        self.set_profile_pic_from_cache()
        self.set_account_info_from_cache()

        # populate sync section
        parent_dir = osp.split(self.mdbx.dropbox_path)[0]
        relative_path = self.rel_path(parent_dir)
        folder_icon = native_item_icon(parent_dir)

        self.comboBoxDropboxPath.clear()
        self.comboBoxDropboxPath.addItem(folder_icon, relative_path)
        self.comboBoxDropboxPath.insertSeparator(1)
        self.comboBoxDropboxPath.addItem(QtGui.QIcon(), "Other...")

        # populate app section
        self.checkBoxStartup.setChecked(self.autostart.enabled)
        self.checkBoxNotifications.setChecked(self.mdbx.notification_level <= 15)
        update_interval = self.mdbx.get_conf("app", "update_notification_interval")
        closest_key = min(
            self._update_interval_mapping,
            key=lambda x: abs(self._update_interval_mapping[x] - update_interval),
        )
        self.comboBoxUpdateInterval.setCurrentIndex(closest_key)

        # populate about section
        year = time.localtime().tm_year
        self.labelVersion.setText(
            self.labelVersion.text().format(__version__, __daemon_version__)
        )
        self.labelUrl.setText(self.labelUrl.text().format(__url__))
        self.labelCopyright.setText(self.labelCopyright.text().format(year, __author__))

    def set_profile_pic_from_cache(self):

        try:
            pixmap = get_masked_image(
                self.mdbx.account_profile_pic_path, size=self._profile_pic_height
            )
        except OSError:
            pixmap = get_masked_image(FACEHOLDER_PATH, size=self._profile_pic_height)

        self.labelUserProfilePic.setPixmap(pixmap)

    def set_account_info_from_cache(self):

        acc_display_name = self.mdbx.get_state("account", "display_name")
        acc_mail = self.mdbx.get_state("account", "email")
        acc_type = self.mdbx.get_state("account", "type")
        acc_space_usage = self.mdbx.get_state("account", "usage")
        acc_space_usage_type = self.mdbx.get_state("account", "usage_type")

        if acc_space_usage_type == "team":
            acc_space_usage += " (Team)"

        # if the display name is longer than 230 pixels, reduce font-size
        default_font = get_scaled_font(1.5)
        if NEW_QT:
            account_display_name_length = QtGui.QFontMetrics(
                default_font
            ).horizontalAdvance(acc_display_name)
        else:
            account_display_name_length = QtGui.QFontMetrics(default_font).width(
                acc_display_name
            )
        if account_display_name_length > 240:
            font = get_scaled_font(scaling=1.5 * 240 / account_display_name_length)
            self.labelAccountName.setFont(font)
        self.labelAccountName.setText(acc_display_name)

        if acc_type != "":
            acc_type_text = ", Dropbox {0}".format(acc_type.capitalize())
        else:
            acc_type_text = ""
        self.labelAccountInfo.setText(acc_mail + acc_type_text)
        self.labelSpaceUsage.setText(acc_space_usage)

    @QtCore.pyqtSlot(int)
    def on_combobox_path(self, idx):
        if idx == 2:
            self.dropbox_folder_dialog.open()

    @QtCore.pyqtSlot(int)
    def on_combobox_update_interval(self, idx):
        self.mdbx.set_conf(
            "app", "update_notification_interval", self._update_interval_mapping[idx]
        )

    @QtCore.pyqtSlot(str)
    def on_new_dbx_folder(self, new_location):

        self.comboBoxDropboxPath.setCurrentIndex(0)
        if not new_location == "":

            new_path = osp.join(new_location, self.default_dirname)

            task = MaestralBackgroundTask(
                parent=self,
                config_name=self.mdbx.config_name,
                target="move_dropbox_directory",
                args=(new_path,),
            )

            task.sig_result.connect(self.on_move_completed)

    @QtCore.pyqtSlot(object)
    def on_move_completed(self, result):

        if isinstance(result, Exception):

            if isinstance(result, OSError):
                title = f"Could not move directory (errno {result.errno})"
                msg = (
                    "Please check if you have permissions to write to the "
                    "selected location."
                )
            else:
                title = "Could not move directory"
                msg = result.args[0]

            msg_box = UserDialog(title, msg, parent=self)
            msg_box.open()  # no need to block with exec
            self.mdbx.start_sync()
        else:
            new_location = self.mdbx.dropbox_path
            self.comboBoxDropboxPath.setItemText(0, self.rel_path(new_location))
            self.comboBoxDropboxPath.setItemIcon(0, native_item_icon(new_location))

    @QtCore.pyqtSlot(int)
    def on_start_on_login_clicked(self, state):
        self.autostart.enabled = state == 2

    @QtCore.pyqtSlot(int)
    def on_notifications_clicked(self, state):
        self.mdbx.notification_level = 15 if state == 2 else 30

    @staticmethod
    def rel_path(path):
        """
        Returns the path relative to the users directory, or the absolute
        path if not in a user directory.
        """
        usr = osp.abspath(osp.join(get_home_dir(), osp.pardir))
        if osp.commonprefix([path, usr]) == usr:
            return osp.relpath(path, usr)
        else:
            return path

    def changeEvent(self, QEvent):

        if QEvent.type() == QtCore.QEvent.PaletteChange:
            self.update_dark_mode()

    def update_dark_mode(self):
        rgb = LINE_COLOR_DARK if is_dark_window() else LINE_COLOR_LIGHT
        line_style = "color: rgb({0}, {1}, {2})".format(*rgb)

        self.line0.setStyleSheet(line_style)
        self.line1.setStyleSheet(line_style)
        self.line2.setStyleSheet(line_style)

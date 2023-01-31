# -*- coding: utf-8 -*-

# external packages
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt

# local imports
from .utils import get_scaled_font, icon_to_pixmap
from .utils import MaestralBackgroundTask
from .resources import APP_ICON_PATH
from .resources.ui_relink_dialog import Ui_RelinkDialog


# noinspection PyArgumentList
class RelinkDialog(QtWidgets.QDialog, Ui_RelinkDialog):
    """
    A dialog to show when Maestral's Dropbox access has expired or has been revoked.
    """

    VALID_MSG = "Verified. Restarting Maestral..."
    INVALID_MSG = "Invalid token"
    CONNECTION_ERR_MSG = "Connection failed"
    PLACEHOLDER_TEXT = "Authorization token"

    EXPIRED = 0
    REVOKED = 1

    def __init__(self, parent, reason=EXPIRED):
        super().__init__()
        self.setupUi(self)

        # noinspection PyTypeChecker
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Sheet
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.CustomizeWindowHint
        )

        self._parent = parent
        self.mdbx = self._parent.mdbx

        # format text labels
        if reason is self.EXPIRED:
            self.titleLabel.setText("Dropbox Access Expired")
            formatted_text = self.infoLabel.text().format(
                "has expired", self.mdbx.get_auth_url()
            )
        elif reason is self.REVOKED:
            self.titleLabel.setText("Dropbox Access Revoked")
            formatted_text = self.infoLabel.text().format(
                "has been revoked", self.mdbx.get_auth_url()
            )
        else:
            raise ValueError(
                '"reason" must be RelinkDialog.EXPIRED or ' "RelinkDialog.REVOKED."
            )
        self.infoLabel.setText(formatted_text)
        self.titleLabel.setFont(get_scaled_font(bold=True))
        self.infoLabel.setFont(get_scaled_font(scaling=0.9))

        # add app icon
        icon = QtGui.QIcon(APP_ICON_PATH)
        pixmap = icon_to_pixmap(icon, self.iconLabel.width(), self.iconLabel.height())
        self.iconLabel.setPixmap(pixmap)

        # format line edit
        self.lineEditAuthCode.setTextMargins(3, 0, 0, 0)

        # connect callbacks
        self.lineEditAuthCode.textChanged.connect(self._update_appearance)
        self.pushButtonCancel.clicked.connect(self.quit)
        self.pushButtonUnlink.clicked.connect(self.delete_creds_and_quit)
        self.pushButtonLink.clicked.connect(self.on_link_clicked)

        # other
        self.pushButtonCancel.setFocus()
        self.adjustSize()

    def quit(self):
        self.set_ui_busy()
        self._parent.quit(stop_daemon=True)

    def delete_creds_and_quit(self):
        self.set_ui_busy()
        self.mdbx.unlink()
        self._parent.quit(stop_daemon=True)

    def _update_appearance(self, text):
        placeholder_text = self.lineEditAuthCode.placeholderText()
        if text == "":
            if placeholder_text == self.PLACEHOLDER_TEXT:
                self.pushButtonLink.setEnabled(False)
                self.lineEditAuthCode.setStyleSheet("")
            elif placeholder_text == self.INVALID_MSG:
                self.pushButtonLink.setEnabled(False)
                self.lineEditAuthCode.setStyleSheet(
                    "color: rgb(205, 0, 0); font: bold;"
                )
            elif placeholder_text == self.CONNECTION_ERR_MSG:
                self.pushButtonLink.setEnabled(False)
                self.lineEditAuthCode.setStyleSheet(
                    "color: rgb(205, 0, 0); font: bold;"
                )
            elif placeholder_text == self.VALID_MSG:
                self.pushButtonLink.setEnabled(False)
                self.pushButtonUnlink.setEnabled(False)
                self.pushButtonCancel.setEnabled(False)
                self.lineEditAuthCode.setStyleSheet(
                    "color: rgb(0, 129, 0); font: bold;"
                )
        else:
            self.pushButtonLink.setEnabled(True)
            self.lineEditAuthCode.setStyleSheet("")

    def on_link_clicked(self):
        token = self.lineEditAuthCode.text()
        if token == "":
            # this should not occur because link button will be inactivate when there
            # is no text in QLineEdit
            return

        self.set_ui_busy()

        self.auth_task = MaestralBackgroundTask(
            parent=self, config_name=self.mdbx.config_name, target="link", args=(token,)
        )
        self.auth_task.sig_result.connect(self.on_link_done)

    def on_link_done(self, res):
        if res == 0:
            self.lineEditAuthCode.setPlaceholderText(self.VALID_MSG)
            QtWidgets.QApplication.processEvents()
            QtCore.QTimer.singleShot(200, self._parent.restart)
        elif res == 1:
            self.lineEditAuthCode.setPlaceholderText(self.INVALID_MSG)
            self.set_ui_idle()
        elif res == 2:
            self.lineEditAuthCode.setPlaceholderText(self.CONNECTION_ERR_MSG)
            self.set_ui_idle()

        self.lineEditAuthCode.setText("")

    def set_ui_busy(self):
        self.progressIndicator.startAnimation()
        self.lineEditAuthCode.setEnabled(False)
        self.pushButtonLink.setEnabled(False)
        self.pushButtonUnlink.setEnabled(False)
        self.pushButtonCancel.setEnabled(False)

    def set_ui_idle(self):
        self.progressIndicator.stopAnimation()
        self.lineEditAuthCode.setEnabled(True)
        self.pushButtonLink.setEnabled(True)
        self.pushButtonUnlink.setEnabled(True)
        self.pushButtonCancel.setEnabled(True)

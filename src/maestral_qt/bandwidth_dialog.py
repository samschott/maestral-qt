# -*- coding: utf-8 -*-

# external packages
from PyQt6 import QtWidgets

# local imports
from .resources.ui_bandwidth_dialog import Ui_BandwidthDialog


MB_2_BYTES = 10**6


class BandwidthDialog(QtWidgets.QDialog, Ui_BandwidthDialog):
    def __init__(self, mdbx, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setModal(True)

        self.mdbx = mdbx

        self.updateButton.clicked.connect(self.on_accepted)
        self.cancelButton.clicked.connect(self.close)

        self.radioButtonDownloadUnlimited.toggled.connect(
            self.on_limit_downloads_toggled
        )
        self.radioButtonUploadUnlimited.toggled.connect(self.on_limit_uploads_toggled)

    def update_gui(self):
        if self.mdbx.bandwidth_limit_down == 0:
            self.radioButtonDownloadUnlimited.setChecked(True)
            self.numberInputDownloadRate.setEnabled(False)
        else:
            self.radioButtonDownloadLimited.setChecked(True)
            self.numberInputDownloadRate.setValue(
                self.mdbx.bandwidth_limit_down / MB_2_BYTES
            )
            self.numberInputDownloadRate.setEnabled(True)

        if self.mdbx.bandwidth_limit_up == 0:
            self.radioButtonUploadUnlimited.setChecked(True)
            self.numberInputUploadRate.setEnabled(False)
        else:
            self.radioButtonUploadLimited.setChecked(True)
            self.numberInputUploadRate.setValue(
                self.mdbx.bandwidth_limit_up / MB_2_BYTES
            )
            self.numberInputUploadRate.setEnabled(True)

    def apply_changes(self):
        if self.radioButtonDownloadUnlimited.isChecked():
            self.mdbx.bandwidth_limit_down = 0.0
        else:
            self.mdbx.bandwidth_limit_down = (
                self.numberInputDownloadRate.value() * MB_2_BYTES
            )

        if self.radioButtonUploadUnlimited.isChecked():
            self.mdbx.bandwidth_limit_up = 0.0
        else:
            self.mdbx.bandwidth_limit_up = (
                self.numberInputUploadRate.value() * MB_2_BYTES
            )

    def on_limit_downloads_toggled(self, value: bool) -> None:
        self.numberInputDownloadRate.setEnabled(not value)

    def on_limit_uploads_toggled(self, value: bool) -> None:
        self.numberInputUploadRate.setEnabled(not value)

    def on_accepted(self, overload=None):
        self.apply_changes()
        self.accept()

    def show(self):
        self.update_gui()
        super().show()

    def open(self):
        self.update_gui()
        super().open()

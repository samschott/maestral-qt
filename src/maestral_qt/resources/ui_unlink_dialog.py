# Form implementation generated from reading ui file '/Users/samschott/Python/maestral-qt/maestral_qt/resources/unlink_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.1.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_UnlinkDialog(object):
    def setupUi(self, UnlinkDialog):
        UnlinkDialog.setObjectName("UnlinkDialog")
        UnlinkDialog.resize(387, 134)
        UnlinkDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(UnlinkDialog)
        self.gridLayout.setHorizontalSpacing(20)
        self.gridLayout.setObjectName("gridLayout")
        self.infoLabel = QtWidgets.QLabel(UnlinkDialog)
        self.infoLabel.setWordWrap(True)
        self.infoLabel.setObjectName("infoLabel")
        self.gridLayout.addWidget(self.infoLabel, 1, 1, 1, 2)
        self.iconLabel = QtWidgets.QLabel(UnlinkDialog)
        self.iconLabel.setMinimumSize(QtCore.QSize(60, 60))
        self.iconLabel.setMaximumSize(QtCore.QSize(60, 60))
        self.iconLabel.setText("")
        self.iconLabel.setObjectName("iconLabel")
        self.gridLayout.addWidget(self.iconLabel, 0, 0, 2, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(UnlinkDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 2, 1, 1)
        self.titleLabel = QtWidgets.QLabel(UnlinkDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.gridLayout.addWidget(self.titleLabel, 0, 1, 1, 2)
        self.progressIndicator = QProgressIndicator(UnlinkDialog)
        self.progressIndicator.setMinimumSize(QtCore.QSize(16, 16))
        self.progressIndicator.setMaximumSize(QtCore.QSize(16, 16))
        self.progressIndicator.setObjectName("progressIndicator")
        self.gridLayout.addWidget(self.progressIndicator, 2, 1, 1, 1, QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.retranslateUi(UnlinkDialog)
        self.buttonBox.accepted.connect(UnlinkDialog.accept)
        self.buttonBox.rejected.connect(UnlinkDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UnlinkDialog)

    def retranslateUi(self, UnlinkDialog):
        _translate = QtCore.QCoreApplication.translate
        UnlinkDialog.setWindowTitle(_translate("UnlinkDialog", "Dialog"))
        self.infoLabel.setText(_translate("UnlinkDialog", "You\'ll still keep your Dropbox folder on this computer, but your files will stop syncing."))
        self.titleLabel.setText(_translate("UnlinkDialog", "Unlink your Dropbox account?"))
from maestral_qt.widgets import QProgressIndicator
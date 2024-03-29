# Form implementation generated from reading ui file '/Users/samschott/Python/maestral-qt/maestral_qt/resources/relink_dialog.ui'
#
# Created by: PyQt6 UI code generator 6.1.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_RelinkDialog(object):
    def setupUi(self, RelinkDialog):
        RelinkDialog.setObjectName("RelinkDialog")
        RelinkDialog.resize(470, 157)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RelinkDialog.sizePolicy().hasHeightForWidth())
        RelinkDialog.setSizePolicy(sizePolicy)
        RelinkDialog.setMinimumSize(QtCore.QSize(470, 0))
        RelinkDialog.setMaximumSize(QtCore.QSize(470, 16777215))
        RelinkDialog.setWindowTitle("")
        self.gridLayout = QtWidgets.QGridLayout(RelinkDialog)
        self.gridLayout.setHorizontalSpacing(15)
        self.gridLayout.setObjectName("gridLayout")
        self.infoLabel = QtWidgets.QLabel(RelinkDialog)
        self.infoLabel.setMinimumSize(QtCore.QSize(0, 50))
        self.infoLabel.setWordWrap(True)
        self.infoLabel.setOpenExternalLinks(True)
        self.infoLabel.setObjectName("infoLabel")
        self.gridLayout.addWidget(self.infoLabel, 1, 1, 1, 6)
        self.iconLabel = QtWidgets.QLabel(RelinkDialog)
        self.iconLabel.setMinimumSize(QtCore.QSize(60, 60))
        self.iconLabel.setMaximumSize(QtCore.QSize(60, 60))
        self.iconLabel.setText("")
        self.iconLabel.setObjectName("iconLabel")
        self.gridLayout.addWidget(self.iconLabel, 0, 0, 2, 1, QtCore.Qt.AlignmentFlag.AlignTop)
        self.pushButtonUnlink = QtWidgets.QPushButton(RelinkDialog)
        self.pushButtonUnlink.setObjectName("pushButtonUnlink")
        self.gridLayout.addWidget(self.pushButtonUnlink, 3, 3, 1, 1)
        self.pushButtonLink = QtWidgets.QPushButton(RelinkDialog)
        self.pushButtonLink.setEnabled(False)
        self.pushButtonLink.setObjectName("pushButtonLink")
        self.gridLayout.addWidget(self.pushButtonLink, 3, 6, 1, 1)
        self.titleLabel = QtWidgets.QLabel(RelinkDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.gridLayout.addWidget(self.titleLabel, 0, 1, 1, 6)
        self.lineEditAuthCode = QtWidgets.QLineEdit(RelinkDialog)
        self.lineEditAuthCode.setText("")
        self.lineEditAuthCode.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.lineEditAuthCode.setObjectName("lineEditAuthCode")
        self.gridLayout.addWidget(self.lineEditAuthCode, 2, 1, 1, 6)
        self.pushButtonCancel = QtWidgets.QPushButton(RelinkDialog)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 3, 5, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(1, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 4, 1, 1)
        self.progressIndicator = QProgressIndicator(RelinkDialog)
        self.progressIndicator.setMinimumSize(QtCore.QSize(16, 16))
        self.progressIndicator.setMaximumSize(QtCore.QSize(16, 16))
        self.progressIndicator.setObjectName("progressIndicator")
        self.gridLayout.addWidget(self.progressIndicator, 3, 1, 1, 1, QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)

        self.retranslateUi(RelinkDialog)
        QtCore.QMetaObject.connectSlotsByName(RelinkDialog)
        RelinkDialog.setTabOrder(self.lineEditAuthCode, self.pushButtonLink)
        RelinkDialog.setTabOrder(self.pushButtonLink, self.pushButtonCancel)
        RelinkDialog.setTabOrder(self.pushButtonCancel, self.pushButtonUnlink)

    def retranslateUi(self, RelinkDialog):
        _translate = QtCore.QCoreApplication.translate
        self.infoLabel.setText(_translate("RelinkDialog", "Your Dropbox access {0}. To continue syncing, please click <a href=\"{1}\">here</a> to retrieve a new authorization token from Dropbox and enter it below."))
        self.pushButtonUnlink.setText(_translate("RelinkDialog", "Unlink and Quit"))
        self.pushButtonLink.setText(_translate("RelinkDialog", "Link"))
        self.titleLabel.setText(_translate("RelinkDialog", "Expired Dropbox access"))
        self.lineEditAuthCode.setPlaceholderText(_translate("RelinkDialog", "Authorization token"))
        self.pushButtonCancel.setText(_translate("RelinkDialog", "Quit"))
from maestral_qt.widgets import QProgressIndicator

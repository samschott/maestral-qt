# Form implementation generated from reading ui file '/Users/samschott/Python/maestral-qt/maestral_qt/resources/sync_issue_widget.ui'
#
# Created by: PyQt6 UI code generator 6.1.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SyncIssueWidget(object):
    def setupUi(self, SyncIssueWidget):
        SyncIssueWidget.setObjectName("SyncIssueWidget")
        SyncIssueWidget.resize(400, 98)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SyncIssueWidget.sizePolicy().hasHeightForWidth())
        SyncIssueWidget.setSizePolicy(sizePolicy)
        SyncIssueWidget.setMinimumSize(QtCore.QSize(400, 0))
        self.verticalLayout = QtWidgets.QVBoxLayout(SyncIssueWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(SyncIssueWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setStyleSheet(".QFrame {\n"
"border: 1px solid rgb(205, 203, 205);\n"
"background-color: rgb(255, 255, 255);\n"
"border-radius: 7px;\n"
"}")
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setContentsMargins(7, 10, 12, 10)
        self.gridLayout.setObjectName("gridLayout")
        self.errorLabel = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.errorLabel.sizePolicy().hasHeightForWidth())
        self.errorLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.errorLabel.setFont(font)
        self.errorLabel.setWordWrap(True)
        self.errorLabel.setObjectName("errorLabel")
        self.gridLayout.addWidget(self.errorLabel, 1, 1, 1, 1)
        self.pathLabel = QElidedLabel(self.frame)
        self.pathLabel.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pathLabel.setFont(font)
        self.pathLabel.setObjectName("pathLabel")
        self.gridLayout.addWidget(self.pathLabel, 0, 1, 1, 1)
        self.iconLabel = QtWidgets.QLabel(self.frame)
        self.iconLabel.setMinimumSize(QtCore.QSize(40, 40))
        self.iconLabel.setMaximumSize(QtCore.QSize(40, 40))
        self.iconLabel.setText("")
        self.iconLabel.setObjectName("iconLabel")
        self.gridLayout.addWidget(self.iconLabel, 0, 0, 2, 1, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.actionButton = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(30)
        sizePolicy.setVerticalStretch(30)
        sizePolicy.setHeightForWidth(self.actionButton.sizePolicy().hasHeightForWidth())
        self.actionButton.setSizePolicy(sizePolicy)
        self.actionButton.setMinimumSize(QtCore.QSize(30, 30))
        self.actionButton.setStyleSheet("QPushButton {\n"
"    border: none;\n"
"    background-color: none;\n"
"    color: rgb(68,133,243);\n"
"    font: bold\n"
"}")
        self.actionButton.setObjectName("actionButton")
        self.gridLayout.addWidget(self.actionButton, 0, 3, 2, 1)
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 2, 1)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(SyncIssueWidget)
        QtCore.QMetaObject.connectSlotsByName(SyncIssueWidget)

    def retranslateUi(self, SyncIssueWidget):
        _translate = QtCore.QCoreApplication.translate
        SyncIssueWidget.setWindowTitle(_translate("SyncIssueWidget", "Form"))
        self.errorLabel.setText(_translate("SyncIssueWidget", "Could not upload:\n"
"Something went wrong with the job on Dropbox’s end. Please verify on the Dropbox website."))
        self.pathLabel.setText(_translate("SyncIssueWidget", "Metamorphosis.txt"))
        self.actionButton.setText(_translate("SyncIssueWidget", "•••"))
from maestral_qt.widgets import QElidedLabel
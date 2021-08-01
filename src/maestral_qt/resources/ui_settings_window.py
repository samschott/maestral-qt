# Form implementation generated from reading ui file '/Users/samschott/Python/maestral-qt/maestral_qt/resources/settings_window.ui'
#
# Created by: PyQt6 UI code generator 6.1.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow):
        SettingsWindow.setObjectName("SettingsWindow")
        SettingsWindow.resize(600, 457)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SettingsWindow.sizePolicy().hasHeightForWidth())
        SettingsWindow.setSizePolicy(sizePolicy)
        SettingsWindow.setMinimumSize(QtCore.QSize(600, 0))
        self.verticalLayout = QtWidgets.QVBoxLayout(SettingsWindow)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayoutMain = QtWidgets.QGridLayout()
        self.gridLayoutMain.setObjectName("gridLayoutMain")
        self.comboBoxUpdateInterval = CustomCombobox(SettingsWindow)
        self.comboBoxUpdateInterval.setObjectName("comboBoxUpdateInterval")
        self.comboBoxUpdateInterval.addItem("")
        self.comboBoxUpdateInterval.addItem("")
        self.comboBoxUpdateInterval.addItem("")
        self.comboBoxUpdateInterval.addItem("")
        self.gridLayoutMain.addWidget(self.comboBoxUpdateInterval, 7, 1, 1, 1)
        self.labelExcludedFoldersTitle = QtWidgets.QLabel(SettingsWindow)
        self.labelExcludedFoldersTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.labelExcludedFoldersTitle.setObjectName("labelExcludedFoldersTitle")
        self.gridLayoutMain.addWidget(self.labelExcludedFoldersTitle, 4, 0, 1, 1)
        self.widgetCLI = QtWidgets.QWidget(SettingsWindow)
        self.widgetCLI.setObjectName("widgetCLI")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widgetCLI)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayoutMain.addWidget(self.widgetCLI, 10, 0, 1, 3)
        self.line0 = QtWidgets.QFrame(SettingsWindow)
        self.line0.setStyleSheet("color: rgb(213, 213, 213)")
        self.line0.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.line0.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line0.setObjectName("line0")
        self.gridLayoutMain.addWidget(self.line0, 11, 0, 1, 3)
        self.pushButtonUnlink = QtWidgets.QPushButton(SettingsWindow)
        self.pushButtonUnlink.setObjectName("pushButtonUnlink")
        self.gridLayoutMain.addWidget(self.pushButtonUnlink, 2, 1, 1, 1)
        self.checkBoxNotifications = QtWidgets.QCheckBox(SettingsWindow)
        self.checkBoxNotifications.setChecked(True)
        self.checkBoxNotifications.setObjectName("checkBoxNotifications")
        self.gridLayoutMain.addWidget(self.checkBoxNotifications, 9, 1, 1, 1)
        self.labelDropboxPathTitle = QtWidgets.QLabel(SettingsWindow)
        self.labelDropboxPathTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.labelDropboxPathTitle.setObjectName("labelDropboxPathTitle")
        self.gridLayoutMain.addWidget(self.labelDropboxPathTitle, 5, 0, 1, 1)
        self.labelAboutTitle = QtWidgets.QLabel(SettingsWindow)
        self.labelAboutTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignTrailing)
        self.labelAboutTitle.setObjectName("labelAboutTitle")
        self.gridLayoutMain.addWidget(self.labelAboutTitle, 12, 0, 1, 1)
        self.labelSystemSettings = QtWidgets.QLabel(SettingsWindow)
        self.labelSystemSettings.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.labelSystemSettings.setObjectName("labelSystemSettings")
        self.gridLayoutMain.addWidget(self.labelSystemSettings, 8, 0, 1, 1)
        self.line1 = QtWidgets.QFrame(SettingsWindow)
        self.line1.setMinimumSize(QtCore.QSize(200, 0))
        self.line1.setStyleSheet("color: rgb(213, 213, 213)")
        self.line1.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.line1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line1.setObjectName("line1")
        self.gridLayoutMain.addWidget(self.line1, 3, 0, 1, 3)
        self.verticalLayoutAccountInfo = QtWidgets.QVBoxLayout()
        self.verticalLayoutAccountInfo.setSpacing(2)
        self.verticalLayoutAccountInfo.setObjectName("verticalLayoutAccountInfo")
        self.labelAccountInfo = QtWidgets.QLabel(SettingsWindow)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelAccountInfo.setFont(font)
        self.labelAccountInfo.setObjectName("labelAccountInfo")
        self.verticalLayoutAccountInfo.addWidget(self.labelAccountInfo)
        self.labelSpaceUsage = QtWidgets.QLabel(SettingsWindow)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelSpaceUsage.setFont(font)
        self.labelSpaceUsage.setObjectName("labelSpaceUsage")
        self.verticalLayoutAccountInfo.addWidget(self.labelSpaceUsage)
        self.gridLayoutMain.addLayout(self.verticalLayoutAccountInfo, 1, 1, 1, 2)
        self.labelUserProfilePic = QtWidgets.QLabel(SettingsWindow)
        self.labelUserProfilePic.setText("")
        self.labelUserProfilePic.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignTrailing)
        self.labelUserProfilePic.setObjectName("labelUserProfilePic")
        self.gridLayoutMain.addWidget(self.labelUserProfilePic, 0, 0, 3, 1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.labelUpdateInterval = QtWidgets.QLabel(SettingsWindow)
        self.labelUpdateInterval.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.labelUpdateInterval.setObjectName("labelUpdateInterval")
        self.gridLayoutMain.addWidget(self.labelUpdateInterval, 7, 0, 1, 1)
        self.pushButtonExcludedFolders = QtWidgets.QPushButton(SettingsWindow)
        self.pushButtonExcludedFolders.setObjectName("pushButtonExcludedFolders")
        self.gridLayoutMain.addWidget(self.pushButtonExcludedFolders, 4, 1, 1, 1)
        self.checkBoxStartup = QtWidgets.QCheckBox(SettingsWindow)
        self.checkBoxStartup.setChecked(True)
        self.checkBoxStartup.setObjectName("checkBoxStartup")
        self.gridLayoutMain.addWidget(self.checkBoxStartup, 8, 1, 1, 1)
        self.labelAccountName = QtWidgets.QLabel(SettingsWindow)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.labelAccountName.setFont(font)
        self.labelAccountName.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom|QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft)
        self.labelAccountName.setObjectName("labelAccountName")
        self.gridLayoutMain.addWidget(self.labelAccountName, 0, 1, 1, 2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.labelUrl = QtWidgets.QLabel(SettingsWindow)
        self.labelUrl.setOpenExternalLinks(True)
        self.labelUrl.setObjectName("labelUrl")
        self.gridLayout.addWidget(self.labelUrl, 1, 0, 1, 1)
        self.labelVersion = QtWidgets.QLabel(SettingsWindow)
        self.labelVersion.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.labelVersion.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.labelVersion.setObjectName("labelVersion")
        self.gridLayout.addWidget(self.labelVersion, 0, 0, 1, 1)
        self.labelCopyright = QtWidgets.QLabel(SettingsWindow)
        self.labelCopyright.setStyleSheet("color: rgb(127, 127, 127)")
        self.labelCopyright.setObjectName("labelCopyright")
        self.gridLayout.addWidget(self.labelCopyright, 2, 0, 1, 1)
        self.gridLayoutMain.addLayout(self.gridLayout, 12, 1, 1, 2)
        self.line2 = QtWidgets.QFrame(SettingsWindow)
        self.line2.setStyleSheet("color: rgb(213, 213, 213)")
        self.line2.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.line2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line2.setObjectName("line2")
        self.gridLayoutMain.addWidget(self.line2, 6, 0, 1, 3)
        self.comboBoxDropboxPath = CustomCombobox(SettingsWindow)
        self.comboBoxDropboxPath.setObjectName("comboBoxDropboxPath")
        self.gridLayoutMain.addWidget(self.comboBoxDropboxPath, 5, 1, 1, 1)
        self.gridLayoutMain.setColumnStretch(0, 4)
        self.gridLayoutMain.setColumnStretch(1, 4)
        self.gridLayoutMain.setColumnStretch(2, 3)
        self.verticalLayout.addLayout(self.gridLayoutMain)
        spacerItem1 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(SettingsWindow)
        QtCore.QMetaObject.connectSlotsByName(SettingsWindow)
        SettingsWindow.setTabOrder(self.pushButtonUnlink, self.pushButtonExcludedFolders)
        SettingsWindow.setTabOrder(self.pushButtonExcludedFolders, self.comboBoxDropboxPath)
        SettingsWindow.setTabOrder(self.comboBoxDropboxPath, self.comboBoxUpdateInterval)
        SettingsWindow.setTabOrder(self.comboBoxUpdateInterval, self.checkBoxStartup)
        SettingsWindow.setTabOrder(self.checkBoxStartup, self.checkBoxNotifications)

    def retranslateUi(self, SettingsWindow):
        _translate = QtCore.QCoreApplication.translate
        SettingsWindow.setWindowTitle(_translate("SettingsWindow", "Maestral Settings"))
        self.comboBoxUpdateInterval.setItemText(0, _translate("SettingsWindow", "Daily"))
        self.comboBoxUpdateInterval.setItemText(1, _translate("SettingsWindow", "Weekly"))
        self.comboBoxUpdateInterval.setItemText(2, _translate("SettingsWindow", "Monthly"))
        self.comboBoxUpdateInterval.setItemText(3, _translate("SettingsWindow", "Never"))
        self.labelExcludedFoldersTitle.setText(_translate("SettingsWindow", "Selective sync:"))
        self.pushButtonUnlink.setText(_translate("SettingsWindow", "Unlink this Dropbox..."))
        self.checkBoxNotifications.setText(_translate("SettingsWindow", "Enable notifications"))
        self.labelDropboxPathTitle.setText(_translate("SettingsWindow", "Local Dropbox folder:"))
        self.labelAboutTitle.setText(_translate("SettingsWindow", "About Maestral:"))
        self.labelSystemSettings.setText(_translate("SettingsWindow", "System settings:"))
        self.labelAccountInfo.setText(_translate("SettingsWindow", "mail@outlook.com, Dropbox Business"))
        self.labelSpaceUsage.setText(_translate("SettingsWindow", "31.8% of 1,324,980GB used"))
        self.labelUpdateInterval.setText(_translate("SettingsWindow", "Check for updates:"))
        self.pushButtonExcludedFolders.setText(_translate("SettingsWindow", "Select files and folders..."))
        self.checkBoxStartup.setText(_translate("SettingsWindow", "Start Maestral on login"))
        self.labelAccountName.setText(_translate("SettingsWindow", "User Name"))
        self.labelUrl.setText(_translate("SettingsWindow", "<html><head/><body><p><a href=\"{0}\">{0}</span></a></p></body></html>"))
        self.labelVersion.setText(_translate("SettingsWindow", "GUI v{0}, daemon v{1}"))
        self.labelCopyright.setText(_translate("SettingsWindow", "© 2018-{0}, {1}."))
from maestral_qt.widgets import CustomCombobox

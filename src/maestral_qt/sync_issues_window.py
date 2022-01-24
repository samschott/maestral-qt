# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:23:13 2018

@author: samschott
"""

# system imports
import os.path as osp
import urllib

# external packages
import click
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from .resources import SYNC_ISSUES_WINDOW_PATH, SYNC_ISSUE_WIDGET_PATH, native_item_icon
from .utils import (
    icon_to_pixmap,
    get_scaled_font,
    center_window,
    is_dark_window,
    LINE_COLOR_DARK,
    LINE_COLOR_LIGHT,
)


# noinspection PyArgumentList
class SyncIssueWidget(QtWidgets.QWidget):
    """
    A widget to graphically display a Maestral sync issue.
    """

    def __init__(self, sync_err, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(SYNC_ISSUE_WIDGET_PATH, self)

        self.sync_err = sync_err

        self.errorLabel.setFont(get_scaled_font(scaling=0.85))
        self.update_dark_mode()  # set appropriate item icon and colors in style sheet

        self.pathLabel.setText(osp.basename(self.sync_err["local_path"]))
        self.errorLabel.setText(
            self.sync_err["title"] + ":\n" + self.sync_err["message"]
        )

        def request_context_menu():
            self.actionButton.customContextMenuRequested.emit(self.actionButton.pos())

        self.actionButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.actionButton.pressed.connect(request_context_menu)
        self.actionButton.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pos):

        self.actionButtonContextMenu = QtWidgets.QMenu()
        a0 = self.actionButtonContextMenu.addAction("View in folder")
        a1 = self.actionButtonContextMenu.addAction("View on dropbox.com")

        a0.setEnabled(osp.exists(self.sync_err["local_path"]))

        a0.triggered.connect(self._go_to_local_path)
        a1.triggered.connect(self._go_to_online)
        self.actionButtonContextMenu.exec_(self.mapToGlobal(pos))

    @QtCore.pyqtSlot()
    def _go_to_local_path(self):
        click.launch(self.sync_err["local_path"], locate=True)

    @QtCore.pyqtSlot()
    def _go_to_online(self):
        dbx_address = "https://www.dropbox.com/preview"
        file_address = urllib.parse.quote(self.sync_err["dbx_path"])
        click.launch(dbx_address + file_address)

    def changeEvent(self, QEvent):
        if QEvent.type() == QtCore.QEvent.PaletteChange:
            self.update_dark_mode()

    def update_dark_mode(self):
        # update style sheet with new colors
        line_rgb = LINE_COLOR_DARK if is_dark_window() else LINE_COLOR_LIGHT
        bg_color = self.palette().color(QtGui.QPalette.Base)
        bg_color_rgb = [bg_color.red(), bg_color.green(), bg_color.blue()]
        self.frame.setStyleSheet(
            """
        .QFrame {{
            border: 1px solid rgb({0},{1},{2});
            background-color: rgb({3},{4},{5});
            border-radius: 7px;
        }}""".format(
                *line_rgb, *bg_color_rgb
            )
        )

        # update item icons (the system may supply different icons in dark mode)
        icon = native_item_icon(self.sync_err["local_path"])
        pixmap = icon_to_pixmap(icon, self.iconLabel.width(), self.iconLabel.height())
        self.iconLabel.setPixmap(pixmap)


# noinspection PyArgumentList
class SyncIssueWindow(QtWidgets.QWidget):
    """
    A widget to graphically display all Maestral sync issues.
    """

    def __init__(self, mdbx, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(SYNC_ISSUES_WINDOW_PATH, self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.mdbx = mdbx
        self.sync_issue_widgets = []

        self.refresh_gui()

        center_window(self)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.refresh_gui)
        self.update_timer.start(1000)  # every 1 sec

    def refresh_gui(self):

        sync_errors_list = self.mdbx.sync_errors  # get a new copy

        self.clear()

        if len(sync_errors_list) == 0:
            no_issues_label = QtWidgets.QLabel("No sync issues :)")
            self.verticalLayout.addWidget(no_issues_label)
            self.sync_issue_widgets.append(no_issues_label)

        for issue in sync_errors_list:
            self.add_issue(issue)

    def add_issue(self, sync_issue):

        issue_widget = SyncIssueWidget(sync_issue)
        self.sync_issue_widgets.append(issue_widget)
        self.verticalLayout.addWidget(issue_widget)

    def clear(self):

        while self.verticalLayout.itemAt(0):
            item = self.verticalLayout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.sync_issue_widgets.clear()

    def show(self):
        self.update_timer.start()
        return super().show()

    def close(self):
        self.update_timer.stop()
        return super().close()

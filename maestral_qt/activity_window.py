# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:23:13 2018

@author: samschott
"""

# system imports
import os.path as osp
import urllib
from datetime import datetime

# external packages
import click
from PyQt5 import QtCore, QtGui, QtWidgets, uic

# local imports
from .resources import (
    SYNC_ISSUES_WINDOW_PATH,
    SYNC_EVENT_WIDGET_PATH,
    native_item_icon,
    native_folder_icon,
)
from .utils import (
    icon_to_pixmap,
    center_window,
    get_scaled_font,
    is_dark_window,
    LINE_COLOR_DARK,
    LINE_COLOR_LIGHT,
)


# noinspection PyArgumentList
class SyncEventWidget(QtWidgets.QWidget):
    """
    A widget to graphically display a Maestral sync event.
    """

    def __init__(self, sync_event, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(SYNC_EVENT_WIDGET_PATH, self)

        self.sync_event = sync_event

        self.update_dark_mode()  # set appropriate item icon and colors in style sheet
        self.filenameLabel.setFont(get_scaled_font(0.9))
        self.infoLabel.setFont(get_scaled_font(0.9))

        dirname, filename = osp.split(self.sync_event["local_path"])
        parent_dir = osp.basename(dirname)
        change_type = self.sync_event["change_type"].capitalize()

        dt = datetime.fromtimestamp(
            self.sync_event["change_time"] or self.sync_event["sync_time"]
        )
        change_time = dt.strftime("%d %b %Y %H:%M")

        self.filenameLabel.setText(filename)
        self.infoLabel.setText(f"{change_type} {change_time} • {parent_dir}")

        def request_context_menu():
            self.actionButton.customContextMenuRequested.emit(self.actionButton.pos())

        self.actionButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.actionButton.pressed.connect(request_context_menu)
        self.actionButton.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pos):

        self.actionButtonContextMenu = QtWidgets.QMenu()
        a0 = self.actionButtonContextMenu.addAction("View in folder")
        a1 = self.actionButtonContextMenu.addAction("View on dropbox.com")

        exists = osp.exists(self.sync_event["local_path"])
        a0.setEnabled(exists)
        a1.setEnabled(exists)

        a0.triggered.connect(self._go_to_local_path)
        a1.triggered.connect(self._go_to_online)
        self.actionButtonContextMenu.exec_(self.mapToGlobal(pos))

    @QtCore.pyqtSlot()
    def _go_to_local_path(self):
        click.launch(self.sync_event["local_path"], locate=True)

    @QtCore.pyqtSlot()
    def _go_to_online(self):
        dbx_address = "https://www.dropbox.com/preview"
        file_address = urllib.parse.quote(self.sync_event["dbx_path"])
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
        if self.sync_event["item_type"] == "file":
            icon = native_item_icon(self.sync_event["local_path"])
        else:
            icon = native_folder_icon()
        pixmap = icon_to_pixmap(icon, self.iconLabel.width(), self.iconLabel.height())
        self.iconLabel.setPixmap(pixmap)


# noinspection PyArgumentList
class ActivityWindow(QtWidgets.QWidget):
    """
    A widget to graphically display all Maestral sync history.
    """

    def __init__(self, mdbx, parent=None):
        super().__init__(parent=parent)
        uic.loadUi(SYNC_ISSUES_WINDOW_PATH, self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Maestral Activity")

        self.mdbx = mdbx
        self._ids = set()

        self.refresh_gui()

        center_window(self)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.refresh_gui)
        self.update_timer.start(1000)  # every 1 sec

    @QtCore.pyqtSlot()
    def refresh_gui(self):

        for event in self.mdbx.get_history():
            if event["id"] not in self._ids:
                event_widget = SyncEventWidget(event)
                self.verticalLayout.insertWidget(0, event_widget)
                self._ids.add(event["id"])

    def show(self):
        self.update_timer.start()
        return super().show()

    def close(self):
        self.update_timer.stop()
        return super().close()

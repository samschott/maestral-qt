# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:23:13 2018

@author: samschott
"""
# system imports
import sys
import os
import re
import platform

# external packages
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QBrush, QImage, QPainter, QPixmap
from Pyro5.errors import ConnectionClosedError

# maestral modules
from maestral.daemon import MaestralProxy

# local imports
from .resources import rgb_to_luminance

THEME_DARK = "dark"
THEME_LIGHT = "light"

LINE_COLOR_DARK = (70, 70, 70)
LINE_COLOR_LIGHT = (213, 213, 213)

IS_BUNDLE = getattr(sys, "frozen", False)
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"
IS_MACOS_BUNDLE = IS_BUNDLE and IS_MACOS
IS_LINUX_BUNDLE = IS_BUNDLE and IS_LINUX


thread_pool = QtCore.QThreadPool()
thread_pool.setMaxThreadCount(10)


# ======================================================================================
# Helper functions
# ======================================================================================


def is_empty(dirname):
    """Checks if a directory is empty."""

    try:
        with os.scandir(dirname) as sciter:
            next(sciter)
    except StopIteration:
        return True

    return False


def elide_string(string, font=None, pixels=200, side="right"):
    """
    Elides a string to fit into the given width.

    :param str string: String to elide.
    :param font: Font to calculate size. If not given, the current style's default font
        for a QLabel is used.
    :param int pixels: Maximum width in pixels.
    :param str side: Side to truncate. Can be 'right' or 'left', defaults to 'right'.
    :return: Truncated string.
    :rtype: str
    """

    if not font:
        font = QtWidgets.QLabel().font()

    metrics = QtGui.QFontMetrics(font)
    mode = Qt.ElideRight if side == "right" else Qt.ElideLeft

    return metrics.elidedText(string, mode, pixels)


def get_scaled_font(scaling=1.0, bold=False, italic=False):
    """
    Returns the current style's default font for a QLabel but scaled by the given
    factor.

    :param float scaling: Scaling factor.
    :param bool bold: Sets the returned font to bold (defaults to ``False``)
    :param bool italic: Sets the returned font to italic (defaults to ``False``)
    :return: Scaled font.
    :rtype: QFont
    """
    label = QtWidgets.QLabel()
    font = label.font()
    font.setBold(bold)
    font.setItalic(italic)
    font_size = round(font.pointSize() * scaling)
    # noinspection PyTypeChecker
    font.setPointSize(font_size)

    return font


url_regex = re.compile(
    r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
)


def markup_urls(string):
    """
    Find any URLs in a string and wrap them in html a tags.

    :param str string: String to parse.
    :return: Marked-up string.
    """

    matches = url_regex.findall(string)

    for match in matches:
        url = "".join(match)
        href = f'<a href="{url}">{url}</a>'
        string = string.replace(url, href)

    return string


# noinspection PyArgumentList
def icon_to_pixmap(icon, width, height=None):
    """Converts a given icon to a pixmap. Automatically adjusts to high-DPI scaling.

    :param icon: Icon to convert.
    :param int width: Target point height.
    :param int height: Target point height.
    :return: ``QPixmap`` instance.
    """
    height = height or width

    is_hidpi = QtCore.QCoreApplication.testAttribute(Qt.AA_UseHighDpiPixmaps)
    pr = QtWidgets.QApplication.instance().devicePixelRatio()

    if not is_hidpi:
        width = width * pr
        height = height * pr
    pixmap = icon.pixmap(width, height)
    if not is_hidpi:
        pixmap.setDevicePixelRatio(pr)

    return pixmap


# noinspection PyArgumentList
def center_window(widget):
    """
    Centers the given widget on screen.

    :param widget: QtWidgets.QWidget
    """
    screen = QtWidgets.QApplication.primaryScreen()
    geometry = screen.availableGeometry()

    x = (geometry.width() - widget.width()) / 2
    y = (geometry.height() - widget.height()) / 3

    widget.move(x, y)


# noinspection PyArgumentList, PyTypeChecker, PyCallByClass
def get_masked_image(path, size=64, overlay_text=""):
    """
    Returns a pixmap from an image file masked with a smooth circle.
    The returned pixmap will have a size of *size* × *size* pixels.

    :param str path: Path to image file.
    :param int size: Target size. Will be the diameter of the masked image.
    :param str overlay_text: Overlay text. This will be shown in white sans-serif on top
        of the image.
    :return: Masked image with overlay text.
    :rtype: QPixmap
    """

    with open(path, "rb") as f:
        imgdata = f.read()

    imgtype = path.split(".")[-1]

    # Load image and convert to 32-bit ARGB (adds an alpha channel):
    image = QImage.fromData(imgdata, imgtype)
    image.convertToFormat(QImage.Format_ARGB32)

    # Crop image to a square:
    imgsize = min(image.width(), image.height())
    rect = QRect(
        (image.width() - imgsize) / 2,
        (image.height() - imgsize) / 2,
        imgsize,
        imgsize,
    )
    image = image.copy(rect)

    # Create the output image with the same dimensions and an alpha channel
    # and make it completely transparent:
    out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
    out_img.fill(Qt.transparent)

    # Create a texture brush and paint a circle with the original image onto
    # the output image:
    brush = QBrush(image)  # Create texture brush
    painter = QPainter(out_img)  # Paint the output image
    painter.setBrush(brush)  # Use the image texture brush
    painter.setPen(Qt.NoPen)  # Don't draw an outline
    painter.setRenderHint(QPainter.Antialiasing, True)  # Use AA
    painter.drawEllipse(0, 0, imgsize, imgsize)  # Actually draw the circle

    if overlay_text:
        # draw text
        font = QtGui.QFont("Arial Rounded MT Bold")
        font.setPointSize(imgsize * 0.4)
        painter.setFont(font)
        painter.setPen(Qt.white)
        painter.drawText(QRect(0, 0, imgsize, imgsize), Qt.AlignCenter, overlay_text)

    painter.end()  # We are done (segfault if you forget this)

    # Convert the image to a pixmap and rescale it.  Take pixel ratio into
    # account to get a sharp image on retina displays:
    pr = QtWidgets.QApplication.instance().devicePixelRatio()
    pm = QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    pm = pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    return pm


# noinspection PyArgumentList
def window_theme():
    """
    :return: THEME_LIGHT or THEME_DARK, corresponding to current user's UI theme.
    :rtype: bool
    """
    w = QtWidgets.QWidget()
    bg_color = w.palette().color(QtGui.QPalette.Background)
    bg_color_rgb = [bg_color.red(), bg_color.green(), bg_color.blue()]
    luminance = rgb_to_luminance(*bg_color_rgb)

    return THEME_LIGHT if luminance >= 0.4 else THEME_DARK


def is_dark_window():
    """Returns ``True`` if windows have a dark UI theme."""
    return window_theme() == THEME_DARK


# ======================================================================================
# Threading
# ======================================================================================


class WorkerEmitter(QtCore.QObject):
    sig_result = QtCore.pyqtSignal(object)
    sig_done = QtCore.pyqtSignal()


class Worker(QtCore.QRunnable):
    """A worker object. To be used in QThreads."""

    def __init__(self, target=None, args=None, kwargs=None):
        super().__init__()
        self._target = target
        self._args = args or ()
        self._kwargs = kwargs or {}
        self.emitter = WorkerEmitter()

    def run(self):

        try:

            res = self._target(*self._args, **self._kwargs)

            if hasattr(res, "__next__"):
                while True:
                    try:
                        next_res = next(res)
                        self.emitter.sig_result.emit(next_res)
                    except StopIteration:
                        return
            else:
                self.emitter.sig_result.emit(res)
        except Exception as exc:
            self.emitter.sig_result.emit(exc)
        finally:
            self.emitter.sig_done.emit()


class MaestralWorker(Worker):
    """A worker object for Maestral. It uses a separate Maestral proxy to prevent
    the main connection from blocking."""

    def __init__(self, config_name="maestral", target=None, args=None, kwargs=None):
        self.config_name = config_name
        self.connection = None
        super().__init__(target, args, kwargs)

    def run(self):

        try:
            with MaestralProxy(self.config_name) as proxy:

                self.connection = proxy._m._pyroConnection

                func = proxy.__getattr__(self._target)

                res = func(*self._args, **self._kwargs)

                if hasattr(res, "__next__"):
                    while True:
                        try:
                            next_res = next(res)
                            self.emitter.sig_result.emit(next_res)
                        except StopIteration:
                            return
                else:
                    self.emitter.sig_result.emit(res)

        except ConnectionClosedError:
            pass
        except Exception as exc:
            self.emitter.sig_result.emit(exc)
        finally:
            self.connection = None
            self.emitter.sig_done.emit()


class BackgroundTask(QtCore.QObject):
    """A utility class to manage a worker thread."""

    sig_result = QtCore.pyqtSignal(object)
    sig_done = QtCore.pyqtSignal()

    def __init__(
        self, parent=None, target=None, args=None, kwargs=None, autostart=True
    ):
        super().__init__(parent)
        self._target = target
        self._args = args or ()
        self._kwargs = kwargs or {}
        self.worker = None

        if autostart:
            self.start()

    def start(self):

        self.worker = Worker(target=self._target, args=self._args, kwargs=self._kwargs)
        self.worker.emitter.sig_result.connect(self.sig_result.emit)
        self.worker.emitter.sig_done.connect(self.sig_done.emit)
        thread_pool.start(self.worker)


class MaestralBackgroundTask(BackgroundTask):
    """A utility class to manage a worker thread. It uses a separate Maestral proxy
    to prevent the main connection from blocking."""

    def __init__(
        self,
        parent=None,
        config_name="maestral",
        target=None,
        args=None,
        kwargs=None,
        autostart=True,
    ):
        self.config_name = config_name
        super().__init__(parent, target, args, kwargs, autostart)

    def start(self):

        self.worker = MaestralWorker(
            config_name=self.config_name,
            target=self._target,
            args=self._args,
            kwargs=self._kwargs,
        )

        self.worker.emitter.sig_result.connect(self.sig_result.emit)
        self.worker.emitter.sig_done.connect(self.sig_done.emit)
        thread_pool.start(self.worker)

    def cancel(self):
        # brute force termination by closing the socket
        if self.worker and self.worker.connection:
            self.worker.connection.close()

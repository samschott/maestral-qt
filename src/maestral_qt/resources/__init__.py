# -*- coding: utf-8 -*-

import os
import os.path as osp
import platform
from importlib.resources import path

from PyQt6 import QtWidgets, QtCore, QtGui

_icon_provider = QtWidgets.QFileIconProvider()
_tmp_file_for_ext = dict()


def resource_path(name):
    """Returns the resource path as a string. Extracts the resource if necessary."""
    return str(path("maestral_qt.resources", name).__enter__())


APP_ICON_PATH = resource_path("maestral.png")
FACEHOLDER_PATH = resource_path("faceholder.png")

THEME_DARK = "dark"
THEME_LIGHT = "light"


def _get_desktop():
    """
    Determines the current desktop environment. This is used for instance to decide
    which keyring backend is preferred to store the auth token.

    :returns: 'gnome', 'kde', 'xfce', 'cocoa', '' or any other string if the desktop
        $XDG_CURRENT_DESKTOP if the desktop environment is not known to us.
    :rtype: str
    """

    if platform.system() == "Linux":
        current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        desktop_session = os.environ.get("GDMSESSION", "").lower()

        for desktop in ("gnome", "kde", "xfce", "mate"):
            if desktop in current_desktop or desktop in desktop_session:
                return desktop

        return "unknown"

    elif platform.system() == "Darwin":
        return "cocoa"


DESKTOP = _get_desktop()


def native_item_icon(item_path):
    """Returns the system icon for the given file or folder. If there is no item at the
    given path, the systems default file icon will be returned.

    :param str item_path: Path to local item.
    """
    while not osp.exists(item_path):
        # We create a temporary file with the given extension to get the correct icon
        # this is necessary because QFileIconProvider has no API to get an icon for a
        # file extension.
        _, extension = osp.splitext(item_path)
        try:
            item_path = _tmp_file_for_ext[extension]
        except KeyError:
            tmp_file = QtCore.QTemporaryFile(
                osp.join(QtCore.QDir.tempPath(), f"XXXXXX{extension}")
            )
            tmp_file.setAutoRemove(False)
            # open and close to create
            tmp_file.open()
            tmp_file.close()

            item_path = tmp_file.fileName()
            _tmp_file_for_ext[extension] = item_path

    return _icon_provider.icon(QtCore.QFileInfo(item_path))


def native_folder_icon():
    """Returns the system's default folder icon."""
    # use a real folder here because Qt may otherwise
    # return the wrong folder icon in some cases
    return _icon_provider.icon(QtCore.QFileInfo("/usr"))


def native_file_icon():
    """Returns the system's default file icon."""
    # use a real file here because Qt may otherwise
    # return the wrong folder icon in some cases
    return _icon_provider.icon(QtCore.QFileInfo(resource_path("file")))


# noinspection PyCallByClass,PyArgumentList
def system_tray_icon(status, geometry=None):
    """Returns the system tray icon for the given status. The following icons
    will be used:

    1) macOS: Black SVG icons with transparent background. macOS will adapt the
       appearance as necessary. This only works reliably in Qt >= 5.15.
    2) Linux: Any icons installed in the system theme. Maestral will prefer "symbolic"
       icons named "maestral-status-{status}-symbolic" over regular icons named
       "maestral-status-{status}". It will fall back to manually setting the icon in a
       color which contrasts the background color of the status bar.

    :param str status: Maestral status. Must be 'idle', 'syncing', 'paused',
        'disconnected' 'info' or 'error'.
    :param geometry: Tray icon geometry on screen. If given, this location will be used
        to determine the system tray background color.
    """
    allowed_status = {"idle", "syncing", "paused", "disconnected", "info", "error"}
    if status not in allowed_status:
        raise ValueError(f"status must be in {allowed_status}")

    if platform.system() == "Darwin":
        # use SVG icon with automatic color
        icon = QtGui.QIcon(resource_path(f"maestral_tray-{status}-dark.svg"))
        icon.setIsMask(True)

    else:
        # Prefer icons from theme if installed / existing. Fall back to loading our own
        # SVG icon with a color contrasting the status bar.
        theme_icon_name = f"maestral_tray-{status}"
        theme_icon_name_symbolic = f"maestral_tray-{status}-symbolic"

        # Prefer "symbolic" icons where the appearance is adapted by the platform
        # automatically. Specs for symbolic icons and their use in the system tray
        # vary between platforms. Fall back to regular icons instead.
        if QtGui.QIcon.hasThemeIcon(theme_icon_name_symbolic):
            icon = QtGui.QIcon.fromTheme(theme_icon_name_symbolic)
        elif QtGui.QIcon.hasThemeIcon(theme_icon_name):
            icon = QtGui.QIcon.fromTheme(theme_icon_name)
        else:
            icon = QtGui.QIcon()

        if icon.isNull():
            color = "light" if is_dark_status_bar(geometry) else "dark"

            # We create our icon from a pixmap instead of the SVG directly, this works
            # around https://bugreports.qt.io/browse/QTBUG-53550.
            pixmap = QtGui.QPixmap(resource_path(f"maestral_tray-{status}-{color}.svg"))
            icon = QtGui.QIcon(pixmap)

    return icon


# noinspection PyArgumentList
def systray_theme(icon_geometry=None):
    """
    Returns one of THEME_LIGHT or THEME_DARK, corresponding to the current status bar
    color.

    ``icon_geometry`` provides the geometry (location and dimensions) of the tray icon.
    If not given, we try to guess the location of the system tray.
    """

    # ---- check for the status bar color ----------------------------------------------

    # see if we can trust returned pixel colors
    # (work around for a bug in Qt with KDE where all screenshots return black)

    c0 = _pixel_at(10, 10)
    c1 = _pixel_at(300, 400)
    c2 = _pixel_at(800, 800)

    if not c0 == c1 == c2 == (0, 0, 0):  # we can trust pixel colors from screenshots
        if not icon_geometry or icon_geometry.isEmpty():
            # ---- guess the location of the status bar --------------------------------

            primary_screen = QtGui.QGuiApplication.primaryScreen()

            rec_screen = primary_screen.geometry()
            rec_available = primary_screen.availableGeometry()

            # convert to QRegion for subtraction
            region_screen = QtGui.QRegion(rec_screen)
            region_available = QtGui.QRegion(rec_available)

            # subtract and convert back to QRect
            task_bar_rect = region_screen.subtracted(region_available).boundingRect()

            px = task_bar_rect.left() + 2
            py = task_bar_rect.bottom() - 2

        else:  # use the given location from icon_geometry
            px = icon_geometry.left()
            py = icon_geometry.bottom()

        # get pixel luminance from icon corner or status bar
        pixel_rgb = _pixel_at(px, py)
        lum = rgb_to_luminance(*pixel_rgb)

        return THEME_LIGHT if lum >= 0.4 else THEME_DARK

    else:
        # ---- give up, default to dark ------------------------------------------------
        return THEME_DARK


def is_dark_status_bar(icon_geometry=None):
    """Detects the current status bar brightness and returns ``True`` for a dark status
    bar. ``icon_geometry`` provides the geometry (location and dimensions) of the tray
    icon. If not given, we try to guess the location of the system tray."""
    return systray_theme(icon_geometry) == THEME_DARK


def rgb_to_luminance(r, g, b, base=256):
    """
    Calculates luminance of a color, on a scale from 0 to 1, meaning that 1 is the
    highest luminance. r, g, b arguments values should be in 0..256 limits, or base
    argument should define the upper limit otherwise.
    """
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / base


# noinspection PyArgumentList
def _pixel_at(x, y):
    """
    Returns (r, g, b) color code for a pixel with given coordinates (each value is in
    0..256 limits)
    """
    screen = QtGui.QGuiApplication.primaryScreen()
    color = screen.grabWindow(0, x, y, 1, 1).toImage().pixel(0, 0)

    return ((color >> 16) & 0xFF), ((color >> 8) & 0xFF), (color & 0xFF)

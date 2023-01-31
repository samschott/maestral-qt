# -*- coding: utf-8 -*-

# system imports
import sys
import os
import time
from traceback import format_exception
from subprocess import Popen
from datetime import timedelta, datetime
from shlex import quote

# external packages
import click
from PyQt6 import QtCore, QtWidgets, QtGui

# maestral modules
from maestral.constants import (
    IDLE,
    SYNCING,
    PAUSED,
    CONNECTING,
    CONNECTED,
    SYNC_ERROR,
    ERROR,
)
from maestral.daemon import (
    start_maestral_daemon_process,
    stop_maestral_daemon_process,
    MaestralProxy,
    Start,
    CommunicationError,
)
from maestral.exceptions import (
    KeyringAccessError,
    NoDropboxDirError,
    TokenExpiredError,
    TokenRevokedError,
    MaestralApiError,
    UpdateCheckError,
    NotLinkedError,
)

# local imports
from . import __url__
from .setup_dialog import SetupDialog
from .relink_dialog import RelinkDialog
from .dropbox_location_dialog import DropboxLocationDialog
from .settings_window import SettingsWindow
from .activity_window import ActivityWindow
from .sync_issues_window import SyncIssueWindow
from .resources import system_tray_icon, APP_ICON_PATH
from .utils import (
    BackgroundTask,
    MaestralBackgroundTask,
    elide_string,
    markup_urls,
    IS_MACOS,
    IS_BUNDLE,
)
from .widgets import (
    BackgroundTaskProgressDialog,
    UserDialog,
    show_dialog,
    show_stacktrace_dialog,
    show_update_dialog,
)
from .autostart import AutoStart


# noinspection PyTypeChecker,PyArgumentList
class MaestralGuiApp(QtWidgets.QSystemTrayIcon):
    """A Qt GUI for the Maestral daemon."""

    mdbx = None
    _started = False

    _context_menu_visible = False

    PAUSE_TEXT = "Pause Syncing"
    RESUME_TEXT = "Resume Syncing"

    icon_mapping = {
        IDLE: "idle",
        SYNCING: "syncing",
        PAUSED: "paused",
        CONNECTED: "idle",
        CONNECTING: "disconnected",
        SYNC_ERROR: "info",
        ERROR: "error",
    }

    def __init__(self, config_name="maestral"):
        super().__init__()

        self.config_name = config_name

        self._n_sync_errors = None
        self._current_icon = None

        self.settings_window = None
        self.sync_issues_window = None
        self.rebuild_dialog = None
        self._progress_dialog = None

        self.statusAction = None
        self.accountEmailAction = None
        self.accountUsageAction = None
        self.syncIssuesAction = None
        self.pauseAction = None
        self.activityAction = None

        self.loading_done = False

        self.autostart = AutoStart(self.config_name)

        self.icons = self.load_tray_icons()
        self.setIcon(CONNECTING)
        self.show_when_systray_available()

        self.menu = QtWidgets.QMenu()
        self.menu.setSeparatorsCollapsible(False)
        self.setContextMenu(self.menu)

        self.setup_ui_unlinked()

        self.check_for_updates_timer = QtCore.QTimer()
        self.check_for_updates_timer.timeout.connect(self.auto_check_for_updates)
        self.check_for_updates_timer.start(30 * 60 * 1000)  # every 30 min

        self.menu.aboutToShow.connect(self._onContextMenuAboutToShow)
        self.menu.aboutToHide.connect(self._onContextMenuAboutToHide)

        # schedule periodic updates
        self._wait_for_status = MaestralBackgroundTask(
            parent=self,
            config_name=self.config_name,
            target="status_change_longpoll",
            autostart=False,
        )
        self._wait_for_status.sig_result.connect(self.update_ui)

    def setIcon(self, icon_name):
        icon = self.icons.get(icon_name, self.icons[SYNCING])
        if self._current_icon != icon_name:
            self._current_icon = icon_name
            super().setIcon(icon)

    def _onContextMenuAboutToShow(self):
        self._context_menu_visible = True
        if self.loading_done:
            self.update_status()

    def _onContextMenuAboutToHide(self):
        self._context_menu_visible = False

    def update_ui(self):
        if self.loading_done:
            try:
                self.update_status()
                self.update_error()
            except CommunicationError:
                self.quit()
            else:
                self._wait_for_status.start()

    def show_when_systray_available(self):
        # If available, show icon, otherwise, set a timer to check back later.
        # This is a workaround for https://bugreports.qt.io/browse/QTBUG-61898
        if self.isSystemTrayAvailable():
            super().setIcon(self.icon())  # reload icon
            self.show()
        else:
            QtCore.QTimer.singleShot(1000, self.show_when_systray_available)

    def load_tray_icons(self):
        icons = dict()
        for key in self.icon_mapping:
            icons[key] = system_tray_icon(self.icon_mapping[key], self.geometry())

        return icons

    def load_maestral(self):
        self.mdbx = self.get_or_start_maestral_daemon()

        try:
            pending_link = self.mdbx.pending_link
        except KeyringAccessError:
            self.update_error()
            return

        pending_folder = self.mdbx.pending_dropbox_folder

        if pending_link or pending_folder:
            self.loading_done = SetupDialog.configureMaestral(self.mdbx)
        else:
            self.loading_done = True

        if self.loading_done:
            self.setup_ui_linked()
            self.mdbx.start_sync()
        else:
            self.quit()

    def get_or_start_maestral_daemon(self):
        res = start_maestral_daemon_process(self.config_name)

        if res == Start.Failed:
            title = "Could not start Maestral"
            message = (
                "Could not start or connect to sync daemon. Please try again "
                "and contact the developer if this issue persists."
            )
            show_dialog(title, message, level="error")
            self.quit()
        elif res == Start.AlreadyRunning:
            self._started = False
        elif res == Start.Ok:
            self._started = True

        return MaestralProxy(self.config_name)

    def setup_ui_unlinked(self):
        self.setToolTip("Not linked.")
        self.menu.clear()

        # ------------- populate context menu -------------------
        openDropboxFolderAction = self.menu.addAction("Open Dropbox Folder")
        openDropboxFolderAction.setEnabled(False)
        openWebsiteAction = self.menu.addAction("Launch Dropbox Website")
        openWebsiteAction.triggered.connect(self.on_website_clicked)

        self.menu.addSeparator()

        statusAction = self.menu.addAction("Setting up...")
        statusAction.setEnabled(False)

        self.menu.addSeparator()

        autostartAction = self.menu.addAction("Start on login")
        autostartAction.setCheckable(True)
        autostartAction.setChecked(self.autostart.enabled)
        autostartAction.triggered.connect(self.autostart.toggle)
        helpAction = self.menu.addAction("Help Center")
        helpAction.triggered.connect(self.on_help_clicked)

        self.menu.addSeparator()

        quitAction = self.menu.addAction("Quit Maestral")
        quitAction.triggered.connect(self.quit)

    def setup_ui_linked(self):
        self.autostart = None
        self.settings_window = SettingsWindow(self, self.mdbx)

        self.setToolTip(IDLE)

        # ------------- populate context menu -------------------

        self.menu.clear()

        openDropboxFolderAction = self.menu.addAction("Open Dropbox Folder")
        openDropboxFolderAction.triggered.connect(self.on_folder_clicked)
        openWebsiteAction = self.menu.addAction("Launch Dropbox Website")
        openWebsiteAction.triggered.connect(self.on_website_clicked)

        self.menu.addSeparator()

        self.accountEmailAction = self.menu.addAction(
            self.mdbx.get_state("account", "email")
        )
        self.accountEmailAction.setEnabled(False)

        self.accountUsageAction = self.menu.addAction(
            self.mdbx.get_state("account", "usage")
        )
        self.accountUsageAction.setEnabled(False)

        self.menu.addSeparator()

        self.statusAction = self.menu.addAction(IDLE)
        self.statusAction.setEnabled(False)
        self.pauseAction = self.menu.addAction(
            self.RESUME_TEXT if self.mdbx.paused else self.PAUSE_TEXT
        )
        self.pauseAction.triggered.connect(self.on_start_stop_clicked)

        self.activityAction = self.menu.addAction("Show Recent Changes...")
        self.activityAction.triggered.connect(self.on_activity_clicked)

        self.menu.aboutToShow.connect(self.update_snoozed)

        self.menu.addSeparator()

        self.snoozeMenu = self.menu.addMenu("Snooze Notifications")
        self.snooze30 = self.snoozeMenu.addAction("For the next 30 minutes")
        self.snooze60 = self.snoozeMenu.addAction("For the next hour")
        self.snooze480 = self.snoozeMenu.addAction("For the next 8 hours")

        def snooze_for(minutes):
            self.mdbx.notification_snooze = minutes

        self.snooze30.triggered.connect(lambda: snooze_for(30))
        self.snooze60.triggered.connect(lambda: snooze_for(60))
        self.snooze480.triggered.connect(lambda: snooze_for(480))
        self.snoozeSeparator = QtGui.QAction()
        self.snoozeSeparator.setSeparator(True)

        self.resumeNotificationsAction = QtGui.QAction("Turn on notifications")
        self.resumeNotificationsAction.triggered.connect(lambda: snooze_for(0))

        self.syncIssuesAction = self.menu.addAction("Show Sync Issues...")
        self.syncIssuesAction.triggered.connect(self.on_sync_issues_clicked)
        rebuildAction = self.menu.addAction("Rebuild index...")
        rebuildAction.triggered.connect(self.on_rebuild_clicked)

        self.menu.addSeparator()

        preferencesAction = self.menu.addAction("Preferences...")
        preferencesAction.triggered.connect(self.on_settings_clicked)
        updatesAction = self.menu.addAction("Check for Updates...")
        updatesAction.triggered.connect(self.on_check_for_updates_clicked)
        helpAction = self.menu.addAction("Help Center")
        helpAction.triggered.connect(self.on_help_clicked)

        self.menu.addSeparator()

        if self._started:
            quitAction = self.menu.addAction("Quit Maestral")
        else:
            quitAction = self.menu.addAction("Quit Maestral GUI")
        quitAction.triggered.connect(self.quit)

        # --------------- switch to idle icon -------------------
        self.setIcon(IDLE)

        # ------------ subscribe to status updates --------------
        self._wait_for_status.start()

    # callbacks for user interaction

    def auto_check_for_updates(self):
        last_update_check = self.mdbx.get_state("app", "update_notification_last")
        interval = self.mdbx.get_conf("app", "update_notification_interval")
        if interval == 0:  # checks disabled
            return
        elif time.time() - last_update_check > interval:
            checker = MaestralBackgroundTask(
                self, self.mdbx.config_name, "check_for_updates"
            )
            checker.sig_result.connect(self._notify_updates_auto)

    def on_check_for_updates_clicked(self):
        checker = MaestralBackgroundTask(
            self, self.mdbx.config_name, "check_for_updates"
        )
        self._progress_dialog = BackgroundTaskProgressDialog("Checking for Updates")
        self._progress_dialog.show()
        self._progress_dialog.rejected.connect(checker.sig_result.disconnect)

        checker.sig_result.connect(self._progress_dialog.accept)
        checker.sig_result.connect(self._notify_updates_user_requested)

    def _notify_updates_user_requested(self, res):
        if isinstance(res, UpdateCheckError):
            show_dialog(res.title, res.message, level="warning")
        elif res.update_available:
            show_update_dialog(res.latest_release, res.release_notes)
        else:
            message = "Maestral v{} is the newest version available.".format(
                res.latest_release
            )
            show_dialog("You’re up-to-date!", message)

    def _notify_updates_auto(self, res):
        if res.update_available:
            self.mdbx.set_state("app", "update_notification_last", time.time())
            show_update_dialog(res.latest_release, res.release_notes)

    def on_website_clicked(self):
        """Open the Dropbox website."""
        click.launch("https://www.dropbox.com/")

    def on_folder_clicked(self):
        """Open the Dropbox folder."""
        click.launch(self.mdbx.dropbox_path)

    def on_help_clicked(self):
        """Open the Dropbox help website."""
        click.launch(f"{__url__}/docs")

    def on_start_stop_clicked(self):
        """Pause / resume syncing on menu item clicked."""
        try:
            if self.pauseAction.text() == self.PAUSE_TEXT:
                self.mdbx.stop_sync()
                self.pauseAction.setText(self.RESUME_TEXT)
            elif self.pauseAction.text() == self.RESUME_TEXT:
                self.mdbx.start_sync()
                self.pauseAction.setText(self.PAUSE_TEXT)
            elif self.pauseAction.text() == "Start Syncing":
                self.mdbx.start_sync()
                self.pauseAction.setText(self.PAUSE_TEXT)
        except (NotLinkedError, NoDropboxDirError):
            self.restart()

    def on_settings_clicked(self):
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def on_sync_issues_clicked(self):
        self.sync_issues_window = SyncIssueWindow(self.mdbx)
        self.sync_issues_window.show()
        self.sync_issues_window.raise_()
        self.sync_issues_window.activateWindow()
        self.sync_issues_window.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)

    def on_activity_clicked(self):
        self.activity_window = ActivityWindow(self.mdbx)
        self.activity_window.show()
        self.activity_window.raise_()
        self.activity_window.activateWindow()
        self.activity_window.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)

    def on_rebuild_clicked(self):
        self.rebuild_dialog = UserDialog(
            title="Rebuilt Maestral's sync index?",
            message=(
                "Rebuilding the index may take several minutes, depending on the size "
                "of your Dropbox. Any changes to local files will be synced once "
                "rebuilding has completed. If you quit Maestral during the process, "
                "rebuilding will  be resumed on the next launch."
            ),
            button_names=("Rebuild", "Cancel"),
        )
        res = self.rebuild_dialog.exec()
        if res == UserDialog.DialogCode.Accepted:
            self.mdbx.rebuild_index()

    # callbacks to update GUI

    def update_snoozed(self):
        minutes = self.mdbx.notification_snooze

        if minutes > 0:
            eta = datetime.now() + timedelta(minutes=minutes)

            self.snoozeMenu.setTitle(
                "Notifications snoozed until %s" % eta.strftime("%H:%M")
            )
            self.snoozeMenu.insertAction(self.snooze30, self.resumeNotificationsAction)
            self.snoozeMenu.insertAction(self.snooze30, self.snoozeSeparator)
        else:
            self.snoozeMenu.removeAction(self.resumeNotificationsAction)
            self.snoozeMenu.removeAction(self.snoozeSeparator)
            self.snoozeMenu.setTitle("Snooze Notifications")

    def update_status(self):
        """Change icon according to status."""
        n_sync_errors = len(self.mdbx.sync_errors)
        status = self.mdbx.status
        is_paused = self.mdbx.paused

        # update icon
        if n_sync_errors > 0 and status == IDLE:
            new_icon = SYNC_ERROR
        else:
            new_icon = status

        self.setIcon(new_icon)

        # update action texts
        if self.contextMenuVisible():
            if n_sync_errors > 0:
                self.syncIssuesAction.setText(
                    "Show Sync Issues ({0})...".format(n_sync_errors)
                )
            else:
                self.syncIssuesAction.setText("Show Sync Issues...")

            self.pauseAction.setText(self.RESUME_TEXT if is_paused else self.PAUSE_TEXT)
            self.accountUsageAction.setText(self.mdbx.get_state("account", "usage"))
            self.accountEmailAction.setText(self.mdbx.get_state("account", "email"))

            status_short = elide_string(status)
            self.statusAction.setText(status_short)

        # update tooltip
        self.setToolTip(status)

        # cache _n_errors
        self._n_sync_errors = n_sync_errors

    def update_error(self):
        errs = self.mdbx.fatal_errors

        if not errs:
            return
        else:
            self.mdbx.clear_fatal_errors()

        self.setIcon(ERROR)

        if self.pauseAction:
            self.pauseAction.setText(self.RESUME_TEXT)

        if self.statusAction:
            self.statusAction.setText(self.mdbx.status)

        err = errs[-1]

        if isinstance(err, NoDropboxDirError):
            # Show location dialog dialog.
            self._dbx_location_dialog = DropboxLocationDialog(self.mdbx)
            self._dbx_location_dialog.show()
            self._dbx_location_dialog.raise_()

        elif isinstance(err, (TokenRevokedError, TokenExpiredError)):
            # Show relink dialog.

            if isinstance(err, TokenExpiredError):
                reason = RelinkDialog.REVOKED
            else:
                reason = RelinkDialog.EXPIRED

            self._relink_dialog = RelinkDialog(self, reason)
            self._relink_dialog.show()
            self._relink_dialog.raise_()

        elif isinstance(err, MaestralApiError):
            # This is a known error. We show the error message and the corresponding
            # file path, if any.

            message = markup_urls(err.message)
            filename = err.dbx_path or err.local_path

            if filename:
                message = f"Path: {filename}\n{message}"

            show_dialog(err.title, message, level="error")

        else:
            # This is an unexpected error. We show the full stacktrace if available.
            if err.__traceback__:
                details = "".join(
                    format_exception(err.__class__, err, err.__traceback__)
                )
                show_stacktrace_dialog(details)
            else:
                show_dialog("An unexpected error occurred", str(err), level="error")

    def contextMenuVisible(self):
        return self._context_menu_visible

    def quit(self, *args, stop_daemon=None):
        """Quits Maestral.

        :param bool stop_daemon: If ``True``, the sync daemon will be PAUSED when
            quitting the GUI, if ``False``, it will be kept alive. If ``None``, the
            daemon will only be PAUSED if it was started by the GUI (default).
        """
        self._wait_for_status.cancel()

        # stop sync daemon if we started it or ``stop_daemon`` is ``True``
        if stop_daemon or self._started:
            task = BackgroundTask(
                parent=self,
                target=stop_maestral_daemon_process,
                args=(self.config_name,),
            )
            task.sig_result.connect(QtWidgets.QApplication.instance().quit)
        else:
            QtWidgets.QApplication.instance().quit()

    def restart(self):
        """Restarts the Maestral GUI and sync daemon."""
        pid = os.getpid()  # get ID of current process

        if IS_MACOS:
            restart_cmd = "lsof -p {0} +r 1 &>/dev/null; {1} -c {2}"
        else:
            restart_cmd = "tail --pid={0} -f /dev/null; {1} -c {2}"

        if IS_BUNDLE:
            launch_command = sys.executable
        else:
            launch_command = f"{sys.executable} -m maestral_qt"

        Popen(
            restart_cmd.format(pid, launch_command, quote(self.config_name)), shell=True
        )

        # quit Maestral
        self.quit(stop_daemon=True)


# noinspection PyArgumentList
def run(config_name="maestral"):
    """
    This is the main interactive entry point which starts the Qt GUI.

    :param str config_name: Name of Maestral config to run.
    """

    app = QtWidgets.QApplication(["Maestral"])
    app.setWindowIcon(QtGui.QIcon(APP_ICON_PATH))
    app.setQuitOnLastWindowClosed(False)

    maestral_gui = MaestralGuiApp(config_name)
    maestral_gui.load_maestral()
    sys.exit(app.exec())

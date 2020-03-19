# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:23:13 2018

@author: samschott
"""

# system imports
import sys
import os
import logging
import platform
import time
from subprocess import Popen
from datetime import timedelta, datetime

# external packages
import click
from PyQt5 import QtCore, QtWidgets, QtGui

# maestral modules
from maestral import __version__
from maestral.utils.backend import pending_link, pending_dropbox_folder
from maestral.utils.autostart import AutoStart
from maestral.constants import (
    IDLE, SYNCING, PAUSED, STOPPED, DISCONNECTED, SYNC_ERROR, ERROR,
    IS_MACOS_BUNDLE, APP_NAME
)
from maestral.daemon import (
    start_maestral_daemon_process,
    start_maestral_daemon_thread,
    stop_maestral_daemon_process,
    stop_maestral_daemon_thread,
    get_maestral_pid,
    get_maestral_proxy,
    Start,
    Pyro5
)

# local imports
from maestral_qt.settings_window import SettingsWindow
from maestral_qt.sync_issues_window import SyncIssueWindow
from maestral_qt.resources import get_system_tray_icon, DESKTOP, APP_ICON_PATH
from maestral_qt.utils import (
    MaestralBackgroundTask,
    BackgroundTaskProgressDialog,
    UserDialog,
    elide_string,
    IS_MACOS,
    show_stacktrace_dialog,
    show_update_dialog,
    show_dialog,
)

logger = logging.getLogger(__name__)


# noinspection PyTypeChecker,PyArgumentList
class MaestralGuiApp(QtWidgets.QSystemTrayIcon):
    """A Qt GUI for the Maestral daemon."""

    mdbx = None
    _started = False

    _context_menu_visible = False

    PAUSE_TEXT = 'Pause Syncing'
    RESUME_TEXT = 'Resume Syncing'

    icon_mapping = {
        IDLE: 'idle',
        SYNCING: 'syncing',
        PAUSED: 'paused',
        STOPPED: 'error',
        DISCONNECTED: 'disconnected',
        SYNC_ERROR: 'info',
        ERROR: 'error',
    }

    __slots__ = (
        'icons', 'menu', 'recentFilesMenu',
        'settings_window', 'sync_issues_window', 'rebuild_dialog', '_progress_dialog',
        'update_ui_timer', 'check_for_updates_timer',
        'statusAction', 'accountEmailAction', 'accountUsageAction', 'pauseAction', 'syncIssuesAction',
        'autostart', '_current_icon', '_n_sync_errors', '_progress_dialog',
    )

    def __init__(self, config_name='maestral'):
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
        self.recentFilesMenu = None

        self.autostart = AutoStart(self.config_name, gui=True)

        self.icons = self.load_tray_icons()
        self.setIcon(DISCONNECTED)
        self.show_when_systray_available()

        self.menu = QtWidgets.QMenu()
        self.setContextMenu(self.menu)

        self.setup_ui_unlinked()

        self.update_ui_timer = QtCore.QTimer()
        self.update_ui_timer.timeout.connect(self.update_ui)
        self.update_ui_timer.start(2000)  # every 2 sec

        self.check_for_updates_timer = QtCore.QTimer()
        self.check_for_updates_timer.timeout.connect(self.auto_check_for_updates)
        self.check_for_updates_timer.start(30 * 60 * 1000)  # every 30 min

        self.menu.aboutToShow.connect(self._onContextMenuAboutToShow)
        self.menu.aboutToHide.connect(self._onContextMenuAboutToHide)

    def setIcon(self, icon_name):
        icon = self.icons.get(icon_name, self.icons[SYNCING])
        self._current_icon = icon_name
        QtWidgets.QSystemTrayIcon.setIcon(self, icon)

    @QtCore.pyqtSlot()
    def _onContextMenuAboutToShow(self):
        self._context_menu_visible = True
        if self.mdbx:
            self.update_status()
        self.update_ui_timer.setInterval(500)
        if IS_MACOS:
            self.icons = self.load_tray_icons('light')
            self.setIcon(self._current_icon)

    @QtCore.pyqtSlot()
    def _onContextMenuAboutToHide(self):
        self._context_menu_visible = False
        if IS_MACOS:
            self.icons = self.load_tray_icons()
            self.setIcon(self._current_icon)

    def update_ui(self):
        if self.mdbx:
            try:
                self.update_status()
                self.update_error()
            except Pyro5.errors.CommunicationError:
                self.quit()
        if not self.contextMenuVisible():
            self.update_ui_timer.setInterval(2000)

    def show_when_systray_available(self):
        # If available, show icon, otherwise, set a timer to check back later.
        # This is a workaround for https://bugreports.qt.io/browse/QTBUG-61898
        if self.isSystemTrayAvailable():
            self.setIcon(self._current_icon)  # reload icon
            self.show()
        else:
            QtCore.QTimer.singleShot(1000, self.show_when_systray_available)

    def load_tray_icons(self, color=None):

        icons = dict()

        for key in self.icon_mapping:
            icons[key] = get_system_tray_icon(self.icon_mapping[key], color=color)

        return icons

    def load_maestral(self):

        not_linked = pending_link(self.config_name)

        if not_linked or pending_dropbox_folder(self.config_name):
            from maestral_qt.setup_dialog import SetupDialog
            logger.info('Setting up Maestral...')
            done = SetupDialog.configureMaestral(self.config_name, not_linked)
            self._started = True
            if done:
                logger.info('Successfully set up Maestral')
                self.mdbx = get_maestral_proxy(self.config_name)
                self.mdbx.run()
                self.setup_ui_linked()
            else:
                logger.info('Setup aborted.')
                self.quit()
        else:
            self.mdbx = self._get_or_start_maestral_daemon()
            self.setup_ui_linked()

    def _get_or_start_maestral_daemon(self):

        pid = get_maestral_pid(self.config_name)
        if pid:
            self._started = False
        else:
            if IS_MACOS_BUNDLE:
                res = start_maestral_daemon_thread(self.config_name)
            else:
                res = start_maestral_daemon_process(self.config_name)
            if res == Start.Failed:
                title = 'Could not start Maestral'
                message = ('Could not start or connect to sync daemon. Please try again '
                           'and contact the developer if this issue persists.')
                show_dialog(title, message, level='error')
                self.quit()
            elif res == Start.AlreadyRunning:
                self._started = False
            elif res == Start.Ok:
                self._started = True

        return get_maestral_proxy(self.config_name)

    def setup_ui_unlinked(self):

        self.setToolTip('Not linked.')
        self.menu.clear()

        # ------------- populate context menu -------------------
        openDropboxFolderAction = self.menu.addAction('Open Dropbox Folder')
        openDropboxFolderAction.setEnabled(False)
        openWebsiteAction = self.menu.addAction('Launch Dropbox Website')
        openWebsiteAction.triggered.connect(self.on_website_clicked)

        self.menu.addSeparator()

        statusAction = self.menu.addAction('Setting up...')
        statusAction.setEnabled(False)

        self.menu.addSeparator()

        autostartAction = self.menu.addAction('Start on login')
        autostartAction.setCheckable(True)
        autostartAction.setChecked(self.autostart.enabled)
        autostartAction.triggered.connect(self.autostart.toggle)
        helpAction = self.menu.addAction('Help Center')
        helpAction.triggered.connect(self.on_help_clicked)

        self.menu.addSeparator()

        quitAction = self.menu.addAction('Quit Maestral')
        quitAction.triggered.connect(self.quit)

    def setup_ui_linked(self):

        if not self.mdbx:
            return

        self.autostart = None
        self.settings_window = SettingsWindow(self, self.mdbx)

        self.setToolTip(IDLE)

        # ------------- populate context menu -------------------

        self.menu.clear()

        openDropboxFolderAction = self.menu.addAction('Open Dropbox Folder')
        openDropboxFolderAction.triggered.connect(self.on_folder_clicked)
        openWebsiteAction = self.menu.addAction('Launch Dropbox Website')
        openWebsiteAction.triggered.connect(self.on_website_clicked)

        self.menu.addSeparator()

        self.accountEmailAction = self.menu.addAction(self.mdbx.get_state('account', 'email'))
        self.accountEmailAction.setEnabled(False)

        self.accountUsageAction = self.menu.addAction(self.mdbx.get_state('account', 'usage'))
        self.accountUsageAction.setEnabled(False)

        self.menu.addSeparator()

        self.statusAction = self.menu.addAction(IDLE)
        self.statusAction.setEnabled(False)
        self.pauseAction = self.menu.addAction(self.PAUSE_TEXT if self.mdbx.syncing else self.RESUME_TEXT)
        self.pauseAction.triggered.connect(self.on_start_stop_clicked)

        self.recentFilesMenu = self.menu.addMenu('Recently Changed Files')

        self.menu.aboutToShow.connect(self.update_recent_files)
        self.menu.aboutToShow.connect(self.update_snoozed)

        self.menu.addSeparator()

        self.snoozeMenu = self.menu.addMenu('Snooze Notifications')
        self.snooze30 = self.snoozeMenu.addAction('For the next 30 minutes')
        self.snooze60 = self.snoozeMenu.addAction('For the next hour')
        self.snooze480 = self.snoozeMenu.addAction('For the next 8 hours')

        def snooze_for(minutes):
            self.mdbx.notification_snooze = minutes

        self.snooze30.triggered.connect(lambda: snooze_for(30))
        self.snooze60.triggered.connect(lambda: snooze_for(60))
        self.snooze480.triggered.connect(lambda: snooze_for(480))
        self.snoozeSeparator = QtWidgets.QAction()
        self.snoozeSeparator.setSeparator(True)

        self.resumeNotificationsAction = QtWidgets.QAction('Turn on notifications')
        self.resumeNotificationsAction.triggered.connect(lambda: snooze_for(0))

        self.syncIssuesAction = self.menu.addAction('Show Sync Issues...')
        self.syncIssuesAction.triggered.connect(self.on_sync_issues_clicked)
        rebuildAction = self.menu.addAction('Rebuild index...')
        rebuildAction.triggered.connect(self.on_rebuild_clicked)

        self.menu.addSeparator()

        preferencesAction = self.menu.addAction('Preferences...')
        preferencesAction.triggered.connect(self.on_settings_clicked)
        updatesAction = self.menu.addAction('Check for Updates...')
        updatesAction.triggered.connect(self.on_check_for_updates_clicked)
        helpAction = self.menu.addAction('Help Center')
        helpAction.triggered.connect(self.on_help_clicked)

        self.menu.addSeparator()

        if self._started:
            quitAction = self.menu.addAction('Quit Maestral')
        else:
            quitAction = self.menu.addAction('Quit Maestral GUI')
        quitAction.triggered.connect(self.quit)

        # --------------- switch to idle icon -------------------
        self.setIcon(IDLE)

    # callbacks for user interaction

    @QtCore.pyqtSlot()
    def auto_check_for_updates(self):

        last_update_check = self.mdbx.get_state('app', 'update_notification_last')
        interval = self.mdbx.get_conf('app', 'update_notification_interval')
        if interval == 0:  # checks disabled
            return
        elif time.time() - last_update_check > interval:
            checker = MaestralBackgroundTask(self, self.mdbx.config_name, 'check_for_updates')
            checker.sig_done.connect(self._notify_updates_auto)

    @QtCore.pyqtSlot()
    def on_check_for_updates_clicked(self):

        checker = MaestralBackgroundTask(self, self.mdbx.config_name, 'check_for_updates')
        self._progress_dialog = BackgroundTaskProgressDialog('Checking for Updates')
        self._progress_dialog.show()
        self._progress_dialog.rejected.connect(checker.sig_done.disconnect)

        checker.sig_done.connect(self._progress_dialog.accept)
        checker.sig_done.connect(self._notify_updates_user_requested)

    @QtCore.pyqtSlot(dict)
    def _notify_updates_user_requested(self, res):

        if res['error']:
            show_dialog('Could not check for updates', res['error'], level='warning')
        elif res['update_available']:
            show_update_dialog(res['latest_release'], res['release_notes'])
        elif not res['update_available']:
            message = 'Maestral v{} is the newest version available.'.format(res['latest_release'])
            show_dialog('You’re up-to-date!', message, level='info')

    @QtCore.pyqtSlot(dict)
    def _notify_updates_auto(self, res):

        if res['update_available']:
            self.mdbx.set_state('app', 'update_notification_last', time.time())
            show_update_dialog(res['latest_release'], res['release_notes'])

    @QtCore.pyqtSlot()
    def on_website_clicked(self):
        """Open the Dropbox website."""
        click.launch('https://www.dropbox.com/')

    @QtCore.pyqtSlot()
    def on_folder_clicked(self):
        """Open the Dropbox folder."""
        click.launch(self.mdbx.dropbox_path)

    @QtCore.pyqtSlot()
    def on_help_clicked(self):
        """Open the Dropbox help website."""
        click.launch('https://dropbox.com/help')

    @QtCore.pyqtSlot()
    def on_start_stop_clicked(self):
        """Pause / resume syncing on menu item clicked."""
        if self.pauseAction.text() == self.PAUSE_TEXT:
            self.mdbx.pause_sync()
            self.pauseAction.setText(self.RESUME_TEXT)
        elif self.pauseAction.text() == self.RESUME_TEXT:
            self.mdbx.resume_sync()
            self.pauseAction.setText(self.PAUSE_TEXT)
        elif self.pauseAction.text() == 'Start Syncing':
            self.mdbx.start_sync()
            self.pauseAction.setText(self.PAUSE_TEXT)

    @QtCore.pyqtSlot()
    def update_snoozed(self):
        minutes = self.mdbx.notification_snooze

        if minutes > 0:
            eta = datetime.now() + timedelta(minutes=minutes)

            self.snoozeMenu.setTitle('Notifications snoozed until %s' % eta.strftime('%H:%M'))
            self.snoozeMenu.insertAction(self.snooze30, self.resumeNotificationsAction)
            self.snoozeMenu.insertAction(self.snooze30, self.snoozeSeparator)
        else:
            self.snoozeMenu.removeAction(self.resumeNotificationsAction)
            self.snoozeMenu.removeAction(self.snoozeSeparator)
            self.snoozeMenu.setTitle('Snooze Notifications')

    @QtCore.pyqtSlot()
    def on_settings_clicked(self):
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    @QtCore.pyqtSlot()
    def on_sync_issues_clicked(self):
        self.sync_issues_window = SyncIssueWindow(self.mdbx)
        self.sync_issues_window.show()
        self.sync_issues_window.raise_()
        self.sync_issues_window.activateWindow()
        self.sync_issues_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    @QtCore.pyqtSlot()
    def on_rebuild_clicked(self):
        self.rebuild_dialog = UserDialog(
            title='Rebuilt Maestral\'s sync index?',
            message=(
                'Rebuilding the index may take several minutes, depending on the size of '
                'your Dropbox. Any changes to local files will be synced once rebuilding '
                'has completed. If you quit Maestral during the process, rebuilding will '
                'be resumed on the next launch.'
            ),
            button_names=('Rebuild', 'Cancel')
        )
        res = self.rebuild_dialog.exec_()
        if res == UserDialog.Accepted:
            self.mdbx.rebuild_index()

    # callbacks to update GUI

    @QtCore.pyqtSlot()
    def update_recent_files(self):
        """Update menu with list of recently changed files."""

        # remove old actions
        self.recentFilesMenu.clear()

        # add new actions
        for dbx_path in reversed(self.mdbx.get_state('sync', 'recent_changes')):
            file_name = os.path.basename(dbx_path)
            truncated_name = elide_string(file_name, font=self.menu.font())
            local_path = self.mdbx.to_local_path(dbx_path)
            action = self.recentFilesMenu.addAction(truncated_name)
            action.setData(local_path)
            action.triggered.connect(self.on_recent_file_clicked)

    @QtCore.pyqtSlot()
    def on_recent_file_clicked(self):
        sender = self.sender()
        local_path = sender.data()
        click.launch(local_path, locate=True)

    def update_status(self):
        """Change icon according to status."""

        n_sync_errors = len(self.mdbx.sync_errors)
        status = self.mdbx.status
        is_paused = self.mdbx.paused
        is_stopped = self.mdbx.stopped

        # update icon
        if is_paused:
            new_icon = PAUSED
        elif is_stopped:
            new_icon = ERROR
        elif n_sync_errors > 0 and status == IDLE:
            new_icon = SYNC_ERROR
        else:
            new_icon = status

        self.setIcon(new_icon)

        # update action texts
        if self.contextMenuVisible():
            if n_sync_errors > 0:
                self.syncIssuesAction.setText('Show Sync Issues ({0})...'.format(n_sync_errors))
            else:
                self.syncIssuesAction.setText('Show Sync Issues...')

            self.pauseAction.setText(self.RESUME_TEXT if is_paused else self.PAUSE_TEXT)
            self.accountUsageAction.setText(self.mdbx.get_state('account', 'usage'))
            self.accountEmailAction.setText(self.mdbx.get_state('account', 'email'))

            status_short = elide_string(status)
            self.statusAction.setText(status_short)

        # update sync issues window
        if n_sync_errors != self._n_sync_errors and _is_pyqt_obj(self.sync_issues_window):
            self.sync_issues_window.reload()

        # update tooltip
        self.setToolTip(status)

        # cache _n_errors
        self._n_sync_errors = n_sync_errors

    def update_error(self):
        errs = self.mdbx.maestral_errors

        if not errs:
            return
        else:
            self.mdbx.clear_maestral_errors()

        self.setIcon(ERROR)
        self.pauseAction.setText(self.RESUME_TEXT)
        self.pauseAction.setEnabled(False)
        self.statusAction.setText(self.mdbx.status)

        err = errs[-1]

        if err['type'] in ('RevFileError', 'BadInputError', 'CursorResetError',
                           'InotifyError', 'OutOfMemoryError'):
            self.mdbx.stop_sync()
            show_dialog(err['title'], err['message'], level='error')
        elif err['type'] == 'DropboxDeletedError':
            self.restart()  # will launch into setup dialog
        elif err['type'] == 'DropboxAuthError':
            from maestral_qt.relink_dialog import RelinkDialog
            self._stop_and_exec_relink_dialog(RelinkDialog.REVOKED)
        elif err['type'] == 'TokenExpiredError':
            from maestral_qt.relink_dialog import RelinkDialog
            self._stop_and_exec_relink_dialog(RelinkDialog.EXPIRED)
        else:
            self._stop_and_exec_error_dialog(err)

    def _stop_and_exec_relink_dialog(self, reason):

        self.mdbx.stop_sync()

        from maestral_qt.relink_dialog import RelinkDialog

        relink_dialog = RelinkDialog(self, reason)

        # Call both show and exec: this works around a bug where
        # the dialog does not stay on top on macOS unless show is called.
        relink_dialog.show()
        relink_dialog.exec_()

    def _stop_and_exec_error_dialog(self, err):

        self.mdbx.stop_sync()

        share, auto_share = show_stacktrace_dialog(
            err['traceback'],
            ask_share=not self.mdbx.analytics
        )

        if share:
            import bugsnag
            bugsnag.configure(
                api_key='081c05e2bf9730d5f55bc35dea15c833',
                app_version=__version__,
                auto_notify=False,
                auto_capture_sessions=False,
            )
            bugsnag.notify(
                RuntimeError(err['type']),
                meta_data={
                    'system':
                        {
                            'platform': platform.platform(),
                            'python': platform.python_version(),
                            'gui': f'Qt {QtCore.PYQT_VERSION_STR}',
                            'desktop': DESKTOP,
                        },
                    'original exception': err,
                }
            )

        self.mdbx.analytics = self.mdbx.analytics or auto_share

    def contextMenuVisible(self):
        return self._context_menu_visible

    def setToolTip(self, text):
        # tray icons in macOS should not have tooltips
        QtWidgets.QSystemTrayIcon.setToolTip(self, text)

    def quit(self, *args, stop_daemon=None):
        """Quits Maestral.

        :param bool stop_daemon: If ``True``, the sync daemon will be stopped when
            quitting the GUI, if ``False``, it will be kept alive. If ``None``, the daemon
            will only be stopped if it was started by the GUI (default).
        """
        logger.info('Quitting...')

        # stop update timer to stop communication with daemon
        self.update_ui_timer.stop()

        threaded = os.getpid() == get_maestral_pid(self.config_name)

        # stop sync daemon if we started it or ``stop_daemon`` is ``True``
        # never stop the daemon if it runs in a thread of the current process
        if threaded:
            stop_maestral_daemon_thread(self.config_name)
        elif stop_daemon or self._started:
            stop_maestral_daemon_process(self.config_name)

        # quit
        QtCore.QCoreApplication.quit()
        sys.exit(0)

    def restart(self):
        """Restarts the Maestral GUI and sync daemon."""

        logger.info('Restarting...')

        # schedule restart after current process has quit
        pid = os.getpid()  # get ID of current process
        if IS_MACOS_BUNDLE:
            # noinspection PyUnresolvedReferences
            launch_command = os.path.join(sys._MEIPASS, 'main')
            Popen('lsof -p {0} +r 1 &>/dev/null; {0}'.format(launch_command), shell=True)
        elif IS_MACOS:
            Popen('lsof -p {0} +r 1 &>/dev/null; maestral gui --config-name=\'{1}\''.format(
                pid, self.config_name), shell=True)
        elif platform.system() == 'Linux':
            Popen('tail --pid={0} -f /dev/null; maestral gui --config-name=\'{1}\''.format(
                pid, self.config_name), shell=True)

        # quit Maestral
        self.quit(stop_daemon=True)


def _is_pyqt_obj(obj):
    """Checks if ``obj`` wraps an underlying C/C++ object."""
    if isinstance(obj, QtCore.QObject):
        try:
            obj.parent()
            return True
        except RuntimeError:
            return False
    else:
        return False


# noinspection PyArgumentList
def run(config_name='maestral'):
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    app = QtWidgets.QApplication([APP_NAME])
    app.setWindowIcon(QtGui.QIcon(APP_ICON_PATH))
    app.setQuitOnLastWindowClosed(False)

    maestral_gui = MaestralGuiApp(config_name)
    app.processEvents()  # refresh ui before loading the Maestral daemon
    maestral_gui.load_maestral()
    sys.exit(app.exec())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-name', help='config name', default='maestral')
    args = parser.parse_args()

    run(args.config_name)

"""
Copyright (C) 2026  AnicJov

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import datetime
import platform
from pathlib import Path

from PyQt6.QtCore import QEvent, QSize, Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from pyqtwaitingspinner import SpinDirection, SpinnerParameters, WaitingSpinner

from config import (
    BTN_BIG_H,
    BTN_SMALL_H,
    BTN_SMALL_W,
    DEFAULT_INSTALL_PATH,
    DOWNLOADS_PATH,
)
from gui.dialogs.license_dialog import LicenseDialog
from gui.dialogs.location_dialog import LocationDialog
from gui.dialogs.postinstall_dialog import PostInstallDialog
from gui.dialogs.version_dialog import VersionDialog
from util.fileio import create_shortcuts, resource_path, safe_rm_r
from worker import InstallerWorker


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication, logger) -> None:
        super().__init__()

        self.app = app
        self.logger = logger
        self.logger.connect_gui(self.append_log)
        self.logger.use_root_formatter_for_gui()
        self.worker = None
        self.install_path = None
        self.should_exit = False

        self.set_up_gui()

    def set_up_gui(self) -> None:
        self.setWindowTitle("SADX Coupon Installer")
        self.resize(600, 240)

        icon_path = resource_path("icons/sonic.png")
        self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        top = QHBoxLayout()
        top.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spinner_params = SpinnerParameters(
            roundness=80.0,
            trail_fade_percentage=80.0,
            number_of_lines=45,
            line_length=8,
            line_width=8,
            inner_radius=4,
            revolutions_per_second=1.1,
            color=self.palette().highlight().color(),
            minimum_trail_opacity=0.0,
            spin_direction=SpinDirection.CLOCKWISE,
            center_on_parent=False,
            disable_parent_when_spinning=False,
        )
        self.spinner = WaitingSpinner(central, self.spinner_params)
        self.spinner.setFixedSize(QSize(32, 32))
        top.addWidget(self.spinner)

        v.addLayout(top)

        self.status_label = QLabel("Waiting on user to start installation")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status_label.setFont(QFont("sans-serif", 18))
        self.status_label.setMargin(0)
        top.setSpacing(16)
        top.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(32)
        v.addWidget(self.progress_bar)

        h = QHBoxLayout()
        self.more_btn = QPushButton("More details...")
        self.more_btn.setCheckable(True)
        self.more_btn.setFixedSize(BTN_SMALL_W, BTN_SMALL_H)
        h.addWidget(self.more_btn)
        h.addStretch(1)
        v.addLayout(h)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setVisible(False)
        self.log_view.setFont(QFont("monospace", 8))
        v.addWidget(self.log_view)

        hb = QHBoxLayout()
        self.start_btn = QPushButton("Start Installation")
        self.launch_btn = QPushButton("Play")
        self.launch_btn.setEnabled(False)
        self.cancel_btn = QPushButton("Exit")

        self.start_btn.setFixedHeight(BTN_BIG_H)
        self.launch_btn.setFixedHeight(BTN_BIG_H)
        self.cancel_btn.setFixedHeight(BTN_BIG_H)

        hb.addWidget(self.start_btn)
        hb.addWidget(self.launch_btn)
        hb.addWidget(self.cancel_btn)
        v.addLayout(hb)

        self.more_btn.toggled.connect(self.on_more)
        self.start_btn.clicked.connect(self.on_start)
        self.cancel_btn.clicked.connect(self.cancel_install)
        self.launch_btn.clicked.connect(self.on_launch)

    def post_install_prompt(self) -> None:
        post_install_dialog = PostInstallDialog(self)
        post_install_dialog.exec()
        selected_options = post_install_dialog.selected_options()

        self.logger.info(
            f"Selected post-install options: {selected_options if selected_options else 'None'}"
        )

        if not self.worker:
            self.logger.error("Worker not available for post-install")
            return
        if not self.install_path or not self.install_path.exists():
            raise FileExistsError("Install path is not set")

        if "cleanup" in selected_options:
            safe_rm_r(self.install_path / DOWNLOADS_PATH, log_cb=self.logger.log_cb)

        apps: list[list] = [
            #    Source file name      Renamed file name
            ["Sonic Adventure DX", "sadx.desktop"],
            ["LiveSplit", "livesplit.desktop"],
        ]
        dirs: dict[str, tuple[Path, Path, bool]] = {
            "menu": (
            #   Option name Source dir
                self.install_path,
            #   Dest dir
                Path.home() / ".local" / "share" / "applications",
            #   Rename file
                True,
            ),
            "desktop": (self.install_path, Path.home() / "Desktop", False),
        }
        create_shortcuts(selected_options, apps, dirs, log_cb=self.logger.log_cb)

    def cancel_install(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.request_cancel()
            self.logger.info("Cancellation requested by user, stopping worker...")
            self.status_label.setText("Stopping installation...")
        else:
            self.logger.info("Exiting")
            self.app.exit(0)

    def append_log(self, text: str) -> None:
        self.log_view.insertPlainText(text + "\n")
        self.log_view.moveCursor(QTextCursor.MoveOperation.End)
        self.log_view.ensureCursorVisible()

    # ------------------------- Event Handlers --------------------------
    def on_start(self) -> None:
        # Sequence: show license -> version select -> choose location -> start worker
        self.start_time = datetime.datetime.now()
        self.log_view.clear()

        self.logger.info("-- System info:")
        self.logger.info(f"{platform.system()} {' '.join(platform.architecture())}")
        self.logger.info(f"{platform.freedesktop_os_release()['PRETTY_NAME']}")
        self.logger.info(f"{platform.version()} {platform.release()}")
        self.logger.info(
            f"Python {platform.python_version()} ({' '.join(platform.python_build())})"
        )

        self.logger.info("-- Starting wizard")

        # License
        license_path = resource_path("LICENSE")
        lic_dialog = LicenseDialog(license_path, self)
        if lic_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.logger.info("License accepted")

        # Version
        version_dialog = VersionDialog(self)
        if version_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.version = version_dialog.selected_version()
        if self.version not in ["stable", "legacy", "unstable"]:
            raise IndexError("Invalid version selected")
        self.logger.info(f"Selected install version: {self.version}")

        # Install location
        loc_dialog = LocationDialog(DEFAULT_INSTALL_PATH, self)
        if loc_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.install_path = loc_dialog.selected_path()
        if not self.install_path:
            return
        self.logger.info(f"Selected install location: {self.install_path}")

        # Start worker
        self.start_btn.setEnabled(False)
        self.status_label.setText("Starting installation...")
        self.worker = InstallerWorker(self.install_path, self.logger, self.version)
        self.worker.status.connect(self.on_status)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_ok.connect(self.on_finished_ok)
        self.worker.finished_err.connect(self.on_finished_err)
        self.worker.finished_cancel.connect(self.on_finished_cancel)
        self.worker.start()

        # Update GUI
        self.cancel_btn.setText("Cancel")
        self.spinner.show()
        self.spinner.start()

    def on_status(self, text) -> None:
        self.status_label.setText(text)

    def on_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)

    def on_more(self, checked: bool) -> None:
        self.setFixedHeight(400) if checked else self.setFixedHeight(240)
        self.log_view.setVisible(checked)
        self.more_btn.setText("Hide details" if checked else "More details...")

    def on_finished_ok(self) -> None:
        self.end_time = datetime.datetime.now()
        self.progress_bar.setValue(100)

        self.status_label.setText("Installation finished!")
        self.logger.info(f"{'-' * 50}")
        self.logger.info("-- Installation finished successfully!\n")
        self.logger.info(f"Finished at {self.end_time}")
        time_delta = self.end_time - self.start_time
        self.logger.info(f"Time taken: {time_delta}")
        self.launch_btn.setEnabled(True)

        self.spinner.stop()
        self.spinner.hide()
        self.cancel_btn.setText("Exit")
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Restart Installation")

        self.post_install_prompt()
        self.logger.info(f"{'-' * 21} Done! {'-' * 21}")

    def on_finished_err(self, err: Exception) -> None:
        self.logger.error(f"Installation failed: {err}")
        self.status_label.setText("Installation failed")

        log_file = Path(self.logger.get_log_file())
        self.logger.info(log_file)
        msg = f"Installation failed: {err}\n\n\nSee{f'log {log_file}' if log_file else 'terminal output'} for details"
        QMessageBox.critical(self, "Error", msg)

        self.start_btn.setEnabled(True)
        self.start_btn.setText("Restart Install")
        self.cancel_btn.setText("Exit")
        self.spinner.stop()

    def on_finished_cancel(self) -> None:
        self.logger.info("Worker canceled")
        self.status_label.setText("Installation canceled")
        self.start_btn.setText("Restart Installation")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setText("Exit")
        self.spinner.stop()
        if self.should_exit:
            self.logger.info("Exiting")
            self.app.exit(0)

    def closeEvent(self, event: QEvent) -> None:
        self.on_close_evet(event)

    def quitEvent(self, event: QEvent) -> None:
        self.on_close_evet(event)

    def on_close_evet(self, event: QEvent) -> None:
        if event.type() not in [event.Type.Close, event.Type.Quit]:
            self.logger.warning("Received non close/quit event on closeEvent")

        self.logger.info(
            f"Close event issued {self.worker}.isRunning={self.worker.isRunning() if self.worker else 'None'}"
        )

        if not self.worker or (self.worker and not self.worker.isRunning()):
            self.logger.info("Exiting")
            event.accept()
            return

        reply = QMessageBox.question(
            self,
            "Quit?",
            "Do you want to cancel the installation and quit?",
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.should_exit = True
            self.cancel_install()

        self.should_exit = False
        event.ignore()

    def on_launch(self) -> None:
        # TODO: Launch on separate threads
        if not self.install_path:
            raise RuntimeError("Install path is not set")
        if not self.worker:
            raise RuntimeError("No worker available")

        self.logger.info("Launching game")

        try:
            self.worker.launch_game()
        except Exception as e:
            QMessageBox.warning(self, "Launch Error", f"Could not launch: {e}")

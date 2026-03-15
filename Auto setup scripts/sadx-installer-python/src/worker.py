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

import base64
import os
import time
import traceback
import zipfile
from os.path import dirname
from shutil import which
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QThread, pyqtSignal

from config import *
from util.compression import extract_tar_gz, unzip
from util.exceptions import CancelException
from util.fileio import (
    create_desktop_files,
    create_extras,
    create_launch_scripts,
    make_exec,
    mark_install_version,
    resource_path,
    safe_copy_files,
    safe_makedirs,
)
from util.network import fetch_resource_if_missing, get_latest_url
from util.qlogger import QLogger
from util.shell import open_shell_cmd, run_shell_cmd


class InstallerWorker(QThread):
    status = pyqtSignal(str)
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_ok = pyqtSignal()
    finished_err = pyqtSignal(str)
    finished_cancel = pyqtSignal()

    def __init__(self, install_path: Path, logger: QLogger, install_version: str="stable") -> None:
        super().__init__()
        self.install_path = install_path
        self.install_version = install_version
        self.logger = logger
        self.cancel_requested = False

        # Compute cumulative weight map
        total = sum(w for _, w, _ in STEPS)
        if total != 100 and total != 0:
            # Normalize if not 100 and not zero-finalize case
            factor = 100 / total
            for i in range(len(STEPS)):
                name, w, desc = STEPS[i]
                STEPS[i] = (name, int(round(w * factor)), desc)

    def __repr__(self) -> str:
        return f"InstallerWorker({self.install_version}, {self.install_path})"

    def request_cancel(self) -> None:
        self.cancel_requested = True

    def check_canceled(self) -> None:
        if self.cancel_requested:
            raise CancelException

    def run_step_progress(self, step_index: int, fraction: float) -> None:
        # Fraction between 0..1 for that step
        base = 0
        for i in range(step_index):
            base += STEPS[i][1]
        weight = STEPS[step_index][1]
        overall = int(base + min(1.0, fraction) * weight)
        self.progress.emit(overall)

    def progress_callback(self, index: int) -> Callable[[float], None]:
        return lambda fraction: self.run_step_progress(index, fraction)

    def run(self) -> None:
        try:
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
            self.logger.info(f"Started install on {timestamp}\n{"-"*50}\n")
            self.logger.info(f"Installing version {self.install_version}. Install path: {self.install_path}")
            self.set_install_version_vars(self.install_version)

            for i, (step_name, weight, desc) in enumerate(STEPS):
                self.check_canceled()
                self.status.emit(desc)
                self.logger.info(f"--- Starting step: {step_name} ({desc})")
                function = getattr(self, step_name)
                function(i)
                self.run_step_progress(i, 1.0)
                self.logger.info(f"Completed step: {step_name}")

            self.status.emit("Installation finished!")
            self.logger.info("Installation finished")
            self.progress.emit(100)
            self.finished_ok.emit()
        except CancelException:
            self.finished_cancel.emit()
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"Fatal error: {e}\n\n{tb}")
            self.finished_err.emit(str(e))

# ------------------------- Helpers --------------------------
    def set_env(self) -> None:
        env = os.environ.copy()

        # PyInstaller on Linux prepends its own library dir to LD_LIBRARY_PATH.
        # Child processes like proton/wine should not inherit that.
        ld_orig = env.get("LD_LIBRARY_PATH_ORIG")
        if ld_orig is not None:
            env["LD_LIBRARY_PATH"] = ld_orig
        else:
            env.pop("LD_LIBRARY_PATH", None)

        # These are useful to the AppImage itself, but not to child tools.
        env.pop("APPDIR", None)
        env.pop("APPIMAGE", None)
        env.pop("ARGV0", None)

        # Prevent bundled Python settings from affecting child processes.
        env.pop("PYTHONHOME", None)
        env.pop("PYTHONPATH", None)

        env['WINEPREFIX'] = str(self.install_path / PREFIX_PATH)
        env['WINEDEBUG'] = "fixme-all"
        env['WINE'] = str(self.wine64)

        if self.proton:
            env['STEAM_COMPAT_DATA_PATH'] = str(self.install_path / COMPAT_PATH)
            env['STEAM_COMPAT_CLIENT_INSTALL_PATH'] = str(self.install_path / COMPAT_PATH)
            env['PROTONFIXES_DISABLE'] = "1"

        self.env = env

    def set_install_version_vars(self, version: str) -> None:
        self.coupon_archive = self.install_path / DOWNLOADS_PATH / f"SADX_Coupon_{version}.zip"
        self.proton_archive = self.install_path / DOWNLOADS_PATH / f"Proton-GE_{version}.tar.gz"
        self.livesplit_archive = self.install_path / DOWNLOADS_PATH / f"LiveSplit_{version}.zip"

        self.livesplit_url = LIVESPLIT_STABLE_URL \
            if version in ["stable", "legacy"] \
            else get_latest_url(LIVESPLIT_LATEST_QURL, LIVESPLIT_LATEST_URL)
        self.proton_url = PROTON_STABLE_URL \
            if version in ["stable", "legacy"] \
            else get_latest_url(PROTON_LATEST_QURL, PROTON_LATEST_URL)

        self.livesplit_checksum = LIVESPLIT_STABLE_CHECKSUM if version in ["stable", "legacy"] else ""
        self.proton_checksum = PROTON_STABLE_CHECKSUM if version in ["stable", "legacy"] else ""

        if version == "stable":
            self.coupon_url = COUPON_STABLE_URL
            self.coupon_checksum = COUPON_STABLE_CHECKSUM
            self.winetricks_verbs = WINETRICKS_VERBS_STABLE
        elif version == "legacy":
            self.coupon_url = COUPON_LEGACY_URL
            self.coupon_checksum = COUPON_LEGACY_CHECKSUM
            self.winetricks_verbs = WINETRICKS_VERBS_LEGACY
        elif version == "unstable":
            self.coupon_url = COUPON_UNSTABLE_URL
            self.coupon_checksum = COUPON_UNSTABLE_CHECKSUM
            self.winetricks_verbs = WINETRICKS_VERBS_UNSTABLE
        else:
            raise ValueError("Install version is not `stable`, `legacy`, or `unstable`")

    def detect_and_set_binaries(self) -> None:
        proton_path = self.install_path / PROTON_PATH
        self.proton_dir = list(proton_path.rglob("GE-Proton*"))[0] # Another ugly glob *shrug*

        if not proton_path.exists() or not self.proton_dir.exists():
            raise FileNotFoundError("Proton directory doesn't exist")

        self.proton = self.proton_dir / "proton"
        if not self.proton.exists():
            raise FileNotFoundError("Proton script doesn't exist")
        self.wine = self.proton_dir / "files" / "bin" / "wine"
        if not self.wine.exists():
            self.logger.warning("Falling back to system wine")
            self.wine = "wine"
        self.wine64 = self.proton_dir / "files" / "bin" / "wine64"
        if not self.wine64.exists():
            self.logger.warning("Falling back to system wine64")
            self.wine = "wine"
            self.wine64 = "wine"
        self.winetricks = self.proton_dir / "protonfixes" / "files" / "bin" / "winetricks"
        if not self.winetricks.exists():
            self.logger.warning("Falling back to system winetricks")
            self.winetricks = "winetricks"
        self.run_cmd = [str(self.proton), "run"]
        if not self.proton.exists():
            self.logger.warning("Falling back to system wine for run_cmd")
            self.run_cmd = ["wine"]
        self.wineboot = self.run_cmd + ["wineboot"]
        if not self.proton.exists():
            self.logger.warning("Falling back to system wineboot for wineboot")
            self.wineboot = ["wineboot"]

# ------------------------- Step implementations --------------------------
    def create_dirs(self, index: int) -> None:
        safe_makedirs(self.install_path)
        dirs = [COMPAT_PATH, PROTON_PATH, PREFIX_PATH, DOWNLOADS_PATH]
        for subpath in dirs:
            safe_makedirs(self.install_path / subpath)
        self.logger.info(f"Created directories {str(dirs)} in {self.install_path}")
        self.run_step_progress(index, 1.0)

    def download_proton(self, index: int) -> None:
        fetch_resource_if_missing(
            self.proton_url,
            self.proton_archive,
            "proton archive",
            self.proton_checksum,
            prog_cb=self.progress_callback(index),
            canc_cb=self.check_canceled,
            log_cb=self.logger.log_cb,
        )

    def download_coupon(self, index: int) -> None:
        fetch_resource_if_missing(
            base64.b64decode(self.coupon_url).decode("utf-8"),
            self.coupon_archive,
            "coupon archive",
            self.coupon_checksum,
            prog_cb=self.progress_callback(index),
            canc_cb=self.check_canceled,
            log_cb=self.logger.log_cb,
        )
        if not zipfile.is_zipfile(self.coupon_archive):
            raise RuntimeError("Coupon archive isn't a valid ZIP")

    def download_livesplit(self, index: int) -> None:
        if self.install_version == "stable":
            self.logger.info("Livesplit bundled with coupon for stable install, skipping download")
            self.run_step_progress(index, 1.0)
            return

        fetch_resource_if_missing(
            self.livesplit_url,
            self.livesplit_archive,
            "livesplit archive",
            self.livesplit_checksum,
            prog_cb=self.progress_callback(index),
            canc_cb=self.check_canceled,
            log_cb=self.logger.log_cb,
        )
        if not self.livesplit_archive.exists():
            raise FileNotFoundError("LiveSplit asset not found after download")

    def extract_proton(self, index: int) -> None:
        proton_path = self.install_path / PROTON_PATH

        skip_extraction = False
        if ASSUME_EXTRACTED and len(list(proton_path.rglob("GE-Proton*"))) > 0:
            self.logger.info(f"Skipping extraction of proton {self.proton_archive.name} (assuming already extracted)")
            skip_extraction = True

        try:
            if not skip_extraction:
                extract_tar_gz(self.proton_archive, self.install_path / proton_path,
                           canc_cb=self.check_canceled, prog_cb=self.progress_callback(index), log_cb=self.logger.log_cb)
        except Exception as e:
            self.logger.error(f"Failed to extract proton {self.proton_archive.name} to {proton_path}: {e}")
            raise

        self.logger.info(f"Extracted proton into {self.install_path / PROTON_PATH}")
        self.logger.info("Detecting and setting binaries and evironment")
        self.detect_and_set_binaries()
        self.set_env()

    def create_wine_prefix(self, index: int) -> None:
        run_shell_cmd(self.wineboot, self.env, err_msg="Wineboot faile:", log_cb=self.logger.log_cb)
        self.program_files = self.install_path / PREFIX_PATH / "drive_c" / "Program Files"
        self.sadx_dir = self.install_path / SADX_PATH
        self.run_step_progress(index, 1.0)

    def extract_coupon(self, index: int) -> None:
        skip_extraction = False
        if ASSUME_EXTRACTED and (self.program_files / "SONICADVENTUREDX").exists():
            self.logger.info(f"Skipping extraction of SADX {self.coupon_archive.name} (assuming already extracted)")
            skip_extraction = True

        passwd = base64.b64decode(COUPON_ZIP_PASSWORD)
        self.logger.info("This might take a while depending on your hardware. Please be patient :^)")
        if not skip_extraction:
            unzip(self.coupon_archive, self.program_files, passwd,
                  canc_cb=self.check_canceled, prog_cb=self.progress_callback(index), log_cb=self.logger.log_cb)

    def extract_livesplit(self, index: int) -> None:
        if self.install_version == "stable":
            self.logger.info("Livesplit bundled with stable install. Skipping extraction")
            self.run_step_progress(index, 1.0)
            return

        dest_dir = self.sadx_dir / "TOOLS" / "LiveSplit"

        if dest_dir.exists():
            self.logger.warning("LiveSplit directory already exists! Continuing anyway")

        unzip(self.livesplit_archive, dest_dir, b"",
              canc_cb=self.check_canceled, prog_cb=self.progress_callback(index), log_cb=self.logger.log_cb)

        self.logger.info(f"Extracted LiveSplit to {dest_dir}")
        self.run_step_progress(index, 1.0)

    def ensure_winetricks_prereqs(self, index: int) -> None:
        cab = which("cabextract")
        if not cab:
            cab = resource_path("cabextract/")
            if not (cab / "cabextract").exists():
                raise FileNotFoundError("Bundled cabextract wrapper not found")
            self.logger.warning(f"System cabextract not found. Using bundled version: {cab}")

            self.env["PATH"] = f"{cab}{os.pathsep}{self.env['PATH']}"
            self.env["CABEXTRACT"] = str(cab / "bin" / "cabextract")
            make_exec(cab / "bin" / "cabextract")
            make_exec(cab / "cabextract")
        else:
            self.logger.info(f"System cabextract found: {cab}")

        # Handle true type fonts as well here somehow

        self.run_step_progress(index, 1.0)


    def winetricks_verbs_install(self, index: int) -> None:
        num_verbs = len(self.winetricks_verbs)

        for i, verb in enumerate(self.winetricks_verbs):
            self.check_canceled()
            self.logger.info(f"Installing winetricks verb: {verb}")

            p = run_shell_cmd([str(self.winetricks), "-q", "--optout", verb], self.env,
                              ignore_err=True, err_msg="Winetricks returned code", log_cb=self.logger.log_cb)

            # Winetricks likes to return non-zero on warning messages,
            # so detect non-fatal ones and continue (very crude detection, sometimes false-positive)
            if p.returncode != 0:
                output = (p.stdout or '') + '\n' + (p.stderr or '')
                output = output.lower()
                self.logger.info(f"output: {output}")

                # Treat these patterns as non-fatal warnings (log and continue)
                nonfatal_patterns = [
                    "warning:",
                    "warning: ",
                    "warning: bug:",
                    "you are using a 64-bit wineprefix",
                    "note: command",
                ]

                is_nonfatal = any(pattern in output for pattern in nonfatal_patterns)

                if is_nonfatal:
                    self.logger.warning(f"Non-fatal winetricks warning for {verb}; continuing. (returncode={p.returncode})")
                    self.run_step_progress(index, (i + 1) / num_verbs)
                    continue

                # Otherwise treat as fatal
                self.logger.error(p.stderr or p.stdout or f'Winetricks returned code {p.returncode}')

                # Prompt user to restart install if we don't catch the warning...
                # why is winetricks like this
                raise RuntimeError(f"Winetricks failed for {verb}: { (p.stderr or p.stdout)[:200] }"
                                   "\n\nIf winetricks reported a `warning` instead of an `error` please try installing again.")

            self.run_step_progress(index, (i + 1) / num_verbs)

    def set_dll_override(self, index: int) -> None:
        cmd = self.run_cmd + ["reg", "add", r"HKCU\Software\Wine\DllOverrides", "/v", "d3d8", "/d", "native", "/f"]
        run_shell_cmd(cmd, self.env, err_msg="Failed to set registry override:", log_cb=self.logger.log_cb)
        self.run_step_progress(index, 1.0)

    def finalize(self, index: int) -> None:
        res_path = self.install_path / RESOURCES_PATH
        self.logger.info(f"Moving resources to {res_path}")
        safe_makedirs(res_path)
        safe_makedirs(res_path / "icons")
        resources = [
            "LICENSE",
            "livesplit-livesplit.xml",
            "icons/livesplit.png",
            "icons/sonic.png",
            "icons/timer.png",
            "icons/trainer.ico",
            "icons/openstates.ico",
            "icons/inputdisplay.ico",
        ]
        safe_copy_files(Path(dirname(resource_path("LICENSE"))), res_path, resources)
        self.logger.info(f"Marking install version in {COMPAT_PATH}")
        mark_install_version(self.install_path / COMPAT_PATH, self.install_version)
        create_launch_scripts(self.run_cmd, self.install_path, self.install_version, self.install_path / LAUNCHERS_PATH, log_cb=self.logger.log_cb)
        create_desktop_files(self.install_path, self.install_version, log_cb=self.logger.log_cb)
        create_extras(self.run_cmd, self.install_path, self.env, log_cb=self.logger.log_cb)
        self.run_step_progress(index, 1.0)

    def launch_game(self) -> None:
        game_launcher = self.install_path / LAUNCHERS_PATH / "run_sadx.sh"
        livesplit_launcher = self.install_path / LAUNCHERS_PATH / "run_livesplit.sh"
        env = self.env

        if game_launcher.exists():
            open_shell_cmd(
                ["sh", str(game_launcher)], env, log_cb=self.logger.log_cb
            )
        elif self.install_path:
            game_exe = (
                self.install_path
                / SADX_PATH
                / (
                    "SADXModManager.exe"
                    if self.install_version == "stable"
                    else "SAModManager.exe"
                )
            )
            open_shell_cmd(
                self.run_cmd + [str(game_exe)],
                env,
                log_cb=self.logger.log_cb,
            )
        else:
            self.logger.error("Didn't find a way to run the game")

        QThread.sleep(1)

        if livesplit_launcher.exists():
            open_shell_cmd(
                ["sh", str(livesplit_launcher)], env, log_cb=self.logger.log_cb
            )
        elif self.install_path:
            livesplit_exe = (
                self.install_path / SADX_PATH / "LiveSplit" / "LiveSplit.exe"
            )
            open_shell_cmd(
                self.run_cmd + [str(livesplit_exe)],
                env,
                log_cb=self.logger.log_cb,
            )
        else:
            self.logger.error("Didn't find a way to run LiveSplit")

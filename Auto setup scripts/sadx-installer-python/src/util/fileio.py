""" Copyright (C) 2026  AnicJov

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

import os
import stat
import sys
from hashlib import sha1
from os import chmod, remove, symlink, walk
from os.path import dirname, exists, join, samefile
from pathlib import Path
from shutil import copy, move, rmtree

from config import *
from util.callbacks import callsback, log_cb
from util.logger import LogLevel
from util.shell import run_shell_cmd

@callsback
def resource_path(relative: str) -> Path:
    rel = Path(relative)

    # PyInstaller: works for both onefile and onedir
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS) / "res"
        return base / rel

    # Running from source tree
    base = Path(__file__).resolve().parents[2] / "res"
    if not base.exists():
        log_cb(LogLevel.INFO, f"Resource path not found: {base}, using development path {DEV_RES_PATH}")
        base = Path(DEV_RES_PATH)

    return base / rel

def safe_makedirs(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def safe_move(source: Path, destination: Path) -> None:
    src = source.expanduser().resolve().as_posix()
    dst = destination.expanduser().resolve().as_posix()
    for src_dir, dirs, files in walk(src):
        dst_dir = src_dir.replace(src, dst)
        if not exists(dst_dir):
            safe_makedirs(Path(dst_dir))
        for file in files:
            src_file = join(src_dir, file)
            dst_file = join(dst_dir, file)
            if exists(dst_file):
                if samefile(src_file, dst_file):
                    continue
                remove(dst_file)
            move(src_file, dst_dir)

def safe_symlink(source: Path, destination: Path) -> bool:
    try:
        symlink(source, destination)
        return False
    except FileExistsError:
        remove(destination)
        symlink(source, destination)
        return True

def safe_copy_files(source: Path, destination: Path, files: list[str]) -> None:
    for file in files:
        try:
            safe_makedirs(destination)
            copy(source / file, destination / file, follow_symlinks=True)
        except (FileNotFoundError, OSError):
            continue

def make_exec(file_path: Path) -> None:
    st = os.stat(file_path)
    chmod(file_path, st.st_mode | stat.S_IEXEC)

@callsback
def validate_file_checksum(checksum: str, file: Path) -> bool:
    if not file.exists():
        log_cb(LogLevel.WARNING, f"Can't compute checksum on non-existant file {file}")
        return False
    if not checksum:
        log_cb(LogLevel.WARNING, "Blank checksum passed to validate_file_checksum")
    if not file.exists():
        log_cb(LogLevel.WARNING, "File passed to validate_file_checksum doesn't exist")
    with open(file, 'rb') as f:
        file_hash = sha1(f.read())
        if file_hash.hexdigest() == checksum:
            return True

    log_cb(LogLevel.WARNING, f"Checksum mismatch! E:{checksum} R:{file_hash.hexdigest()}")
    return False

@callsback
def write_launcher(run_cmd: list[str], install_path: Path, script_src: Path, script_dest_path: Path, vars: dict[str, str]) -> Path:
    if not Path(dirname(script_dest_path)).exists():
        raise FileExistsError(f"Script destination path {dirname(script_dest_path)} doesn't exist")

    log_cb(LogLevel.INFO, f"Reading launcher {script_src}")
    try:
        with open(script_src, 'r', encoding="utf-8") as f:
            script: str = f.read()
    except (FileNotFoundError, OSError):
        raise
    log_cb(LogLevel.INFO, f"Read launcher {script_src}: {script[:500]}...")

    base_vars: dict[str, str] = {
        "prefix":  str(install_path / PREFIX_PATH),
        "compat":  str(install_path / COMPAT_PATH),
        "run_cmd": ' '.join([f"\"{part}\"" for part in run_cmd]),
    }

    log_cb(LogLevel.INFO, f"Formatting launcher {script_dest_path} with vars: {base_vars | vars}")
    try:
        with open(script_dest_path, 'w', encoding='utf-8') as f:
            script_formatted: str = str.format_map(script, base_vars | vars)
            f.write(script_formatted)
            f.flush()

        if not script_dest_path.exists():
            raise FileNotFoundError(f"Script file {script_dest_path} was not found after writing")

        make_exec(script_dest_path)

        log_cb(LogLevel.INFO, f"Created launcher script: {script_dest_path}")
    except KeyError as e:
        log_cb(LogLevel.WARNING, f"Couldn't format the script: {script_dest_path}: {e}")
    except (FileExistsError, OSError) as e:
        log_cb(LogLevel.WARNING, f"Failed creating launcher {script_dest_path}: {e}")

    return script_dest_path

@callsback
def create_launch_scripts(run_cmd: list[str], install_path: Path, install_version: str, destination: Path) -> None:
    safe_makedirs(destination)

    game_dir = install_path / SADX_PATH
    game_exe =  game_dir / "SAModManager.exe" if install_version != "legacy" else "SADXModManager.exe"
    livesplit_exe = game_dir / "TOOLS" / "LiveSplit" / "LiveSplit.exe"

    try:
        sadx_vars = {"exe_dir": str(game_dir), "exe_path": str(game_exe)}
        livesplit_vars = {"exe_dir": str(dirname(livesplit_exe)), "exe_path": str(livesplit_exe)}

        write_launcher(run_cmd, install_path, resource_path("launcher.sh"), install_path / LAUNCHERS_PATH / "run_sadx.sh", sadx_vars)
        write_launcher(run_cmd, install_path, resource_path("launcher.sh"), install_path / LAUNCHERS_PATH / "run_livesplit.sh", livesplit_vars)
    except (KeyError, FileExistsError, OSError):
        raise

@callsback
def register_mime_types(env) -> None:
    log_cb(LogLevel.INFO, "Registering MIME types for LiveSplit")
    mime_dir = Path.home() / ".local" / "share" / "mime" / "application"
    mime_filename = "livesplit-livesplit.xml"
    log_cb(LogLevel.INFO, "Ensuring mime directory exists")
    safe_makedirs(mime_dir)
    log_cb(LogLevel.INFO, f"Copying mimetype definition {resource_path(mime_filename)}->{mime_dir / mime_filename}")
    safe_copy_files(Path(dirname(resource_path(mime_filename))), mime_dir, [mime_filename])
    log_cb(LogLevel.INFO, "Running update-mime-database, xdg-mime default")
    run_shell_cmd(["update-mime-database", str(mime_dir)], env, err_msg="Failed to update mime database:")
    run_shell_cmd(["xdg-mime", "default", "livesplit.desktop", "application/x-livesplit-splits", str(mime_dir)], env, err_msg="Failed to set default mime type for lss")
    run_shell_cmd(["xdg-mime", "default", "livesplit.desktop", "application/x-livesplit-layout", str(mime_dir)], env, err_msg="Failed to set default mime type for lsl")
    log_cb(LogLevel.INFO, "Mime type registered")

@callsback
def make_desktop_file(src: Path, dest_path: Path, vars: dict[str, str]) -> None:
    try:
        if not src.exists():
            raise FileNotFoundError(f"Desktop file {src} not found in resources")

        with open(src, 'r', encoding="utf-8") as src_file:
            content = src_file.read()
            formatted_content = content.format_map(vars)
    except KeyError as e:
        log_cb(LogLevel.ERROR, f"Couldn't format desktop file for {dest_path}: {e}")
        return
    except (FileNotFoundError, OSError, ValueError):
        raise

    try:
        with open(dest_path, 'w', encoding="utf-8") as dest_file:
            dest_file.write(formatted_content)
            dest_file.flush()

        if not dest_path.exists():
            raise FileNotFoundError(f"Desktop file {dest_path} not found after writing")

        make_exec(dest_path)

        log_cb(LogLevel.INFO, f"Created desktop entry: {dest_path}")
    except Exception as e:
        log_cb(LogLevel.ERROR, f"Failed to create desktop file {dest_path}: {e}")

@callsback
def create_desktop_files(install_path, install_version) -> None:
    sadx_icon = install_path / RESOURCES_PATH / "icons" / "sonic.png"
    livesplit_icon = install_path / RESOURCES_PATH / "icons" / "livesplit.png"

    if not (sadx_icon.exists() and livesplit_icon.exists()):
        log_cb(LogLevel.ERROR, "Application icons not found")

    sadx_vars = {
        "name": f"Sonic Adventure DX ({install_version.capitalize()})",
        "generic_name": "Sonic Adventure DX: Director's Cut",
        "comment": "Sonic Adventure DX: Director's Cut",
        "keywords": "sadx;sonic",
        "exec": str(install_path / LAUNCHERS_PATH / "run_sadx.sh"),
        "path": str(install_path / LAUNCHERS_PATH),
        "icon": sadx_icon,
        "mime": "",
    }
    livesplit_vars = {
        "name": f"LiveSplit ({install_version.capitalize()})",
        "generic_name": "Speedrun Timer",
        "comment": "LiveSplit Speedrun Timer",
        "keywords": "livesplit;timer;speedrun;split;splits",
        "exec": str(install_path / LAUNCHERS_PATH / "run_livesplit.sh"),
        "path": str(install_path / LAUNCHERS_PATH),
        "icon": livesplit_icon,
        "mime": "application/x-livesplit-splits;application/x-livesplit-layout;",
    }

    make_desktop_file(resource_path("app.desktop"), install_path / "Sonic Adventure DX", sadx_vars)
    make_desktop_file(resource_path("app.desktop"), install_path / "LiveSplit", livesplit_vars)

@callsback
def create_shortcuts(options: list[str], apps: list[list[Path]], dirs: dict[str, tuple[Path, Path, bool]]) -> bool:
    anything_created = False
    for option in options:
        if option in dirs.keys():
            if not dirs[option][0].exists() or not dirs[option][1].exists():
                log_cb(LogLevel.WARNING, f"Link source or destination directories {dirs[option][0]} & {dirs[option][1]} don't exist. Skipping")
                continue
            for app in apps:
                if not (dirs[option][0] / app[0]).exists():
                    log_cb(LogLevel.WARNING, f"Link source {app[0]} doesn't exist. Skipping")
                    continue
                safe_symlink(dirs[option][0] / app[0], dirs[option][1] / app[1 if dirs[option][2] else 0])
                anything_created = True

    return anything_created

@callsback
def safe_rm_r(path: Path) -> bool:
    if not path.exists():
        log_cb(LogLevel.WARNING, f"{path} doesn't exist. Skipping deletion")
        return False

    log_cb(LogLevel.INFO, f"Removing directory {path} recursively")
    rmtree(path)

    return True

def create_app(app_desc: list[str], install_path: Path) -> None:
    vars_desktop = {
        "name": app_desc[0],
        "generic_name": app_desc[0],
        "comment": app_desc[0],
        "keywords": "sadx;speedrun",
        "exec": f"\"{str(install_path / LAUNCHERS_PATH / "launcher_any.sh")}\"" + f" \"{dirname(app_desc[1])}\" \"{app_desc[1]}\"",
        "path": str(install_path / LAUNCHERS_PATH),
        "icon": app_desc[3],
        "mime": "",
    }
    make_desktop_file(resource_path("app.desktop"), install_path / app_desc[2], vars_desktop)

@callsback
def create_extras(run_cmd, install_path: Path, env: dict[str, str]) -> None:
    log_cb(LogLevel.INFO, "Creating SONICADVENTUREDX symlink")
    safe_symlink(install_path / SADX_PATH, install_path / "SONICADVENTUREDX")

    log_cb(LogLevel.INFO, "Creating Tools directory")
    safe_makedirs(install_path / TOOLS_PATH)

    log_cb(LogLevel.INFO, f"Creating arbitrary launcher with env vars: {env}")
    write_launcher(run_cmd, install_path, resource_path("launcher_any.sh"), install_path / LAUNCHERS_PATH / "launcher_any.sh", env)

    log_cb(LogLevel.INFO, "Creating shortcuts for tools")
    tools_prefix: Path = install_path / SADX_PATH / "TOOLS"
    apps: list[list[str]] = [
    #   App name             App executable                                                       Desktop file path               Icon path
        ["SADX IL Timer",    str(tools_prefix / "IL Timer" / "External SADX IL Timer.exe"),       "Tools/IL Timer.desktop",       str(install_path / RESOURCES_PATH / "icons" / "timer.png")],
        ["SADX Open States", str(tools_prefix / "OpenStates" / "SADXOpenStates.exe"),             "Tools/SADXOpenStates.desktop", str(install_path / RESOURCES_PATH / "icons" / "openstates.ico")],
        ["SADX Trainer",     str(tools_prefix / "SADX Trainer" / "SADX Trainer.exe"),             "Tools/SADX Trainer.desktop",   str(install_path / RESOURCES_PATH / "icons" / "trainer.ico")],
        ["Input Display",    str(tools_prefix / "Sonic Input Display" / "SonicInputDisplay.exe"), "Tools/Input Display.desktop",  str(install_path / RESOURCES_PATH / "icons" / "inputdisplay.ico")],
    ]
    for app in apps:
        create_app(app, install_path)

def mark_install_version(dest: Path, install_version: str) -> None:
    with open(dest / "install_version", 'w') as f:
        f.write(install_version)

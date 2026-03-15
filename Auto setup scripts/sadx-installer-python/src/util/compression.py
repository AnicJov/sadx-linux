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

import math
import os
import shutil
import subprocess
import tarfile
import zipfile
from multiprocessing import Event, Process
from os.path import basename, dirname
from pathlib import Path

import pyzipper
from PyQt6.QtCore import QThread

from config import *
from util.callbacks import callsback, canc_cb, log_cb, prog_cb
from util.exceptions import CancelException
from util.fileio import safe_makedirs
from util.logger import LogLevel


@callsback
def extract_tar_gz(archive: Path, dest: Path) -> None:
    if not tarfile.is_tarfile(archive):
        raise FileNotFoundError("{target} is not a valid tar file")

    with tarfile.open(archive, 'r:gz') as tf:
        members = tf.getmembers()
        total = len(members)
        log_amount = LOG_PROGRESS_AMOUNT
        num_extracted = 0
        last_logged = 0
        log_chunk = total // log_amount
        last_logged = 0
        for member in members:
            canc_cb()
            tf.extract(member, path=dest)
            num_extracted += 1
            extracted_percent = num_extracted / total
            prog_cb(extracted_percent)
            if num_extracted - last_logged >= log_chunk:
                log_cb(LogLevel.INFO, f"Extracted {(extracted_percent*100):.1f}% {basename(str(members[last_logged].name))}...{basename(str(member.name))}")
                last_logged = num_extracted
        prog_cb(1.0)

def unzip_file(is_done, archive: Path, files: list[str], destinatnion: Path, password: bytes = b"") -> None:
    zf = zipfile.ZipFile(archive, 'r', allowZip64=True)
    for file in files:
        zf.extract(file, destinatnion, pwd=password)
    zf.close()
    if zf.fp:
        zf.fp.close()
    is_done.set()

def unzip_zipfile(archive: Path, destination: Path, password: bytes) -> None:
    """
    Multithreaded method loosely inspired by https://github.com/Inferno2899/fast_unzip
    although implemented very differently. It's not a pretty function but it works...
    and it's a lot faster than vanilla zipfile or pyzipper, at the cost of CPU usage.
    """

    log_cb(LogLevel.INFO, "Querying CPU count")
    cpu_count = os.cpu_count()
    if not cpu_count or cpu_count == 0:
        raise RuntimeError("Couldn't get number of CPUs on the system")
    log_cb(LogLevel.INFO, f"System has {cpu_count} CPUs")

    process_count = max(cpu_count, 8)

    log_cb(LogLevel.INFO, "Getting file list from archive")
    with zipfile.ZipFile(archive, 'r', allowZip64=True) as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if not infos:
            raise RuntimeError("ZIP archive has 0 files")

        # Validate password / archive by reading 1 byte from the first real file.
        log_cb(LogLevel.INFO, "Validating archive/password")
        with zf.open(infos[0], pwd=password) as f:
            f.read(1)

    log_cb(LogLevel.INFO, "Making destination directories")
    for info in infos:
        safe_makedirs(destination / Path(dirname(info.filename)))

    # Largest files first, then greedy load balancing into worker buckets.
    infos.sort(key=lambda i: i.file_size, reverse=True)
    worker_count = min(process_count, len(infos))
    buckets = [{"size": 0, "files": []} for _ in range(worker_count)]

    for info in infos:
        bucket = min(buckets, key=lambda b: b["size"])
        bucket["files"].append(info.filename)
        bucket["size"] += info.file_size

    jobs = [b["files"] for b in buckets if b["files"]]
    log_cb(LogLevel.INFO, f"Extracting {len(infos)} files with {len(jobs)} workers")

    workers = []
    for files in jobs:
        done = Event()
        proc = Process(target=unzip_file, args=(done, archive, files, destination, password))
        workers.append({
            "done": done,
            "proc": proc,
            "files": files,
            "label": f"{basename(files[0])}...{basename(files[-1])}",
        })
        proc.start()
        QThread.msleep(75)

    log_cb(LogLevel.INFO, f"Started {len(workers)} processes")

    finished = set()
    total = len(workers)
    last_logged = 0
    log_chunk = max(1, math.ceil(total / LOG_PROGRESS_AMOUNT))

    while len(finished) < total:
        try:
            canc_cb()
        except CancelException:
            for w in workers:
                w["proc"].terminate()
            raise

        for i, w in enumerate(workers):
            if i not in finished and w["done"].is_set():
                finished.add(i)
                if len(finished) - last_logged >= log_chunk:
                    log_cb(
                        LogLevel.INFO,
                        f"Extracted {len(finished) / total * 100:.1f}% {w['label']}"
                    )
                    last_logged = len(finished)

        prog_cb(len(finished) / total)
        QThread.msleep(100)

    for w in workers:
        w["proc"].join()

    prog_cb(1.0)

def unzip_pyzipper(archive: Path, destination: Path, password: bytes) -> None:
    with pyzipper.AESZipFile(archive, 'r') as zf:
        files = [file.filename for file in zf.filelist]
        num_extracted = 0
        log_amount = 24
        last_logged = 0
        log_chunk = len(files) // log_amount
        for file in files:
            canc_cb()
            try:
                zf.extract(file, destination, password)
            except TypeError:
                # Fallback in case pyzipper expects string password
                zf.extract(file, destination, str(password))
            num_extracted += 1
            extracted_percent = num_extracted / len(files)
            prog_cb(extracted_percent)
            if num_extracted - last_logged >= log_chunk:
                log_cb(LogLevel.INFO, f"Extracted {extracted_percent*100:.1f}% {basename(files[last_logged])}...{basename(file)}")
                last_logged = num_extracted
    prog_cb(1.0)

def unzip_system(archive: Path, destination: Path, password: bytes) -> None:
    method = None
    if shutil.which("7z"):
        method = "7z"
    if shutil.which("unzip"):
        method = "unzip"
    if not method:
        raise RuntimeError('No suitable system extractor (7z/unzip) found')

    if method == "7z":
        cmd = ["7z", "x", str(archive), f"-p{str(password)}", f"-o{str(destination)}", "-y"]
    else:
        cmd = ["unzip", "-P", str(password), str(archive), "-d", str(destination)]
    log_cb(LogLevel.INFO, f"Attempting extraction with {method}: {' '.join(cmd)}")
    p = subprocess.run(cmd, capture_output=True, text=True)
    log_cb(LogLevel.INFO, p.stdout)
    if p.returncode != 0:
        log_cb(LogLevel.ERROR, p.stderr)
        raise RuntimeError(f"{method} extraction failed: {p.stderr or p.stdout}")

@callsback
def unzip(archive: Path, destination: Path, password: bytes = b"") -> None:
    # Try all the methods in order and hope one works
    try:
        log_cb(LogLevel.INFO, "Trying multiprocess zipfile for extraction")
        unzip_zipfile(archive, destination, password)
        log_cb(LogLevel.INFO, f"Successfully extracted {basename(archive)} with zipfile")
        return
    except NotImplementedError as e:
        log_cb(LogLevel.WARNING, f"Couldn't extract archive {basename(archive)} with zipfile: {e}")

    try:
        log_cb(LogLevel.WARNING, "Falling back to pyzipper for extraction")
        unzip_pyzipper(archive, destination, password)
        log_cb(LogLevel.INFO, f"Successfully extracted {basename(archive)} with pyzipper")
        return
    except NotImplementedError as e:
        log_cb(LogLevel.WARNING, f"Couldn't extract archive {basename(archive)} with pyzipper: {e}")

    try:
        log_cb(LogLevel.WARNING, "Falling back to system tools for extraction")
        unzip_system(archive, destination, password)
        log_cb(LogLevel.INFO, f"Successfully extracted {basename(archive)} with system tools")
    except Exception as e:
        log_cb(LogLevel.ERROR, f"Couldn't extract archive {basename(archive)} with system tools: {e}")

    raise RuntimeError( # Unfort
        'Could not extract coupon archive. '
        'Reason: unsupported compression by Python zipfile and all fallbacks failed. '
        'Install the Python package "pyzipper" (pip install pyzipper) or system package "p7zip-full" (provides 7z) '
        'or "unzip", then try again.'
    )

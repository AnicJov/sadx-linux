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

import requests
import time
from humanize import naturalsize
from pathlib import Path
from os.path import basename, getsize
from util.logger import LogLevel
from util.fileio import validate_file_checksum
from util.callbacks import callsback, log_cb, canc_cb, prog_cb
from config import LOG_PROGRESS_AMOUNT


def get(url: str, **getkwargs) -> requests.Response:
    # We do a little lying
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0"}
    with requests.Session() as s:
        response = s.get(url, headers=headers, **getkwargs)
    
        if not response.ok:
            raise ConnectionError(f"Get {response.url} failed: {response.status_code} {response.reason}")
        
        return response

def download_with_progress(url: str, dest: Path, checksum: str = "") -> bool:
    log_cb(LogLevel.INFO, f"Downloading {url} -> {dest}")
    try:
        response = get(url, stream=True, timeout=60)
        response.raise_for_status()
        total = response.headers.get('content-length')
        f = open(dest, 'wb')

        downloaded = 0
        written = 0
        chunk_size = 16384 if total else 8192
        start_time = time.monotonic()
        prev_time = start_time
        for chunk in response.iter_content(chunk_size):
            canc_cb()
            if chunk:
                now = time.monotonic()
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    written += len(chunk)
                    fraction = written / int(total)
                    prog_cb(fraction)
                else:
                    # If we don't know the size assume 1126MiB for our largest download *shrug*
                    max_total = 1024**3 * 1126
                    fraction = downloaded / max_total
                    prog_cb(fraction)

                prev_dl = downloaded - chunk_size
                est_total = int(total) if total else max_total
                dt = now - prev_time
                rate = downloaded / dt if dt > 0 else 0.0
                if (downloaded * LOG_PROGRESS_AMOUNT) // est_total > (prev_dl * LOG_PROGRESS_AMOUNT) // est_total:
                    log_cb(LogLevel.INFO, f"Downloading {basename(dest)} {(fraction*100):3.2f}% ({naturalsize(downloaded, binary=True)}/{naturalsize(est_total, binary=True)}) {naturalsize(rate, binary=True)}ps")

        prog_cb(1.0)
        log_cb(LogLevel.INFO, f'Download complete {basename(dest)}: {naturalsize(written if total else getsize(dest), binary=True)}')

        f.flush()
        f.close()
        response.close()

        is_valid = validate_file_checksum(checksum, dest)
        if is_valid is RuntimeWarning:
            log_cb(LogLevel.WARNING, is_valid.message)
        if is_valid:
            log_cb(LogLevel.INFO, f"Checksum matches on downloaded file {basename(dest)} = {checksum}")
            return False

        return True
    except TimeoutError as e:
        log_cb(LogLevel.ERROR, f"Timeout while downloading {url}: {e}")
        raise
    except (ConnectionError, BrokenPipeError, requests.RequestException, requests.HTTPError) as e:
        log_cb(LogLevel.ERROR, f"Error while downloading {url}: {e}")
        raise
    except PermissionError as e:
        log_cb(LogLevel.ERROR, f"Permission error while writing target file {url}: {e}")
        raise

@callsback
def fetch_resource_if_missing(url: str, dest: Path, description: str = "resource", checksum="") -> bool:
    log_cb(LogLevel.INFO, f"Checking if {description} exists at {dest}")

    is_valid = validate_file_checksum(checksum, dest)
    if not is_valid:
        log_cb(LogLevel.INFO, f"Existing {description} failed validation; re-downloading.")
        return download_with_progress(url, dest, checksum)
    
    log_cb(LogLevel.INFO, f"Existing {description} validated, skipping download.")
    return True

def get_latest_url(url: str, url_pattern: str) -> str:
    response = get(url, allow_redirects=True)
    version = response.url.split('/')[-1]
    full_url = url_pattern.replace(r"{version}", version)

    return full_url

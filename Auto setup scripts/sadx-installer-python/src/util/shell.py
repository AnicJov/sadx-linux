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

import subprocess
from util.logger import LogLevel
from util.callbacks import callsback, log_cb
from threading import Thread


@callsback
def run_shell_cmd(cmd: list[str], env, capture_output=True, text=True, err_msg: str = "", ignore_err: bool = False) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, env=env, capture_output=capture_output, text=text)

    log_cb(LogLevel.INFO, f"Started command: {' '.join(cmd)}")

    if p.stdout:
        log_cb(LogLevel.INFO, p.stdout)
    if p.stderr:
        log_cb(LogLevel.ERROR, p.stderr) if not ignore_err else log_cb(LogLevel.WARNING, p.stderr)
    if not ignore_err and p.returncode != 0:
        raise RuntimeError(f"{err_msg} {p.returncode} {p.stderr}")

    return p


@callsback
def open_shell_cmd(cmd: list[str], env, capture_output=True, text=True, err_msg: str = "", ignore_err: bool = False) -> None:
    # Ugly code but this function is non-blocking unlike run_shell_cmd
    def _stream_pipe(pipe, level, buffer: list[str]) -> None:
        try:
            for line in iter(pipe.readline, ''):
                if not line:
                    break
                buffer.append(line)
                log_cb(level, line.rstrip('\n'))
        finally:
            pipe.close()

    stdout_pipe = subprocess.PIPE if capture_output else None
    stderr_pipe = subprocess.PIPE if capture_output else None

    p = subprocess.Popen(
        cmd,
        env=env,
        stdout=stdout_pipe,
        stderr=stderr_pipe,
        text=text,
        bufsize=1 if text else -1,
    )

    log_cb(LogLevel.INFO, f"Started command: {' '.join(cmd)}")

    p._stdout_buf = []
    p._stderr_buf = []
    p._stdout_thread = None
    p._stderr_thread = None

    if capture_output and text:
        if p.stdout is not None:
            p._stdout_thread = Thread(
                target=_stream_pipe,
                args=(p.stdout, LogLevel.INFO, p._stdout_buf),
                daemon=True,
            )
            p._stdout_thread.start()

        if p.stderr is not None:
            stderr_level = LogLevel.WARNING if ignore_err else LogLevel.ERROR
            p._stderr_thread = Thread(
                target=_stream_pipe,
                args=(p.stderr, stderr_level, p._stderr_buf),
                daemon=True,
            )
            p._stderr_thread.start()

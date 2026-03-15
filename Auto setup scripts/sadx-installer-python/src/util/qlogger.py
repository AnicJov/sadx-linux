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

import logging
import time
from logging import DEBUG, ERROR, INFO, NOTSET, WARN
from os.path import dirname
from pathlib import Path
from typing import Callable, Optional

from PyQt6.QtCore import QObject, pyqtBoundSignal, pyqtSignal

from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL, LONG_DATE_FORMAT, SHORT_DATE_FORMAT
from util.fileio import safe_makedirs
from util.logger import LogLevel


class QLogger(logging.Logger):
    class _Emitter(QObject):
        log_signal = pyqtSignal(str)

    class _QtSignalHandler(logging.Handler):
        def __init__(self, emitter) -> None:
            super().__init__()
            self._emitter = emitter

        def emit(self, record: logging.LogRecord) -> None:
            try:
                msg = self.format(record)
                self._emitter.log_signal.emit(msg)
            except Exception:
                self.handleError(record)

    def __init__(self, name: str, level: int = logging.NOTSET) -> None:
        super().__init__(name, level)

        self._emitter = QLogger._Emitter()
        self._qt_handler = QLogger._QtSignalHandler(self._emitter)

        self._qt_handler.setFormatter(logging.Formatter("%(message)s"))
        self.addHandler(self._qt_handler)
        self.propagate = True

    @staticmethod
    def from_logger(logger: logging.Logger):
        return QLogger(logger.name, logger.level)

    @property
    def log_signal(self) -> pyqtBoundSignal:
        return self._emitter.log_signal

    def log_cb(self, level: LogLevel, msg: str) -> None:
        if level == LogLevel.INFO:
            self.info(msg)
        elif level == LogLevel.WARNING:
            self.warning(msg)
        elif level == LogLevel.ERROR:
            self.error(msg)
        elif level == LogLevel.DEBUG:
            self.debug(msg)
        else:
            self.log(NOTSET, msg)

    def connect_gui(self, slot: Callable[[str], None]) -> None:
        self._emitter.log_signal.connect(slot)

    def disconnect_gui(self, slot: Optional[Callable[[str], None]] = None) -> None:
        if slot is None:
            self._emitter.log_signal.disconnect()
        else:
            self._emitter.log_signal.disconnect(slot)

    def set_gui_level(self, level: int) -> None:
        self._qt_handler.setLevel(level)

    def set_gui_format(self, fmt: str, style, datefmt: str|None = None, ) -> None:
        self._qt_handler.setFormatter(logging.Formatter(fmt=f"{fmt}\n", datefmt=datefmt, style=style))

    def use_root_formatter_for_gui(self) -> bool:
        root = logging.getLogger()
        for h in root.handlers:
            if h.formatter is not None:
                self._qt_handler.setFormatter(h.formatter)
                return True
        return False

    def get_log_file(self) -> str:
        return self.handlers[1].get_name()


def get_qlogger():
    logging.setLoggerClass(QLogger)
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt=LONG_DATE_FORMAT, force=True)

    safe_makedirs(Path(dirname(LOG_FILE)))
    file_name = str(LOG_FILE).replace(r"{ts_short}", time.strftime(SHORT_DATE_FORMAT))
    file_handler = logging.FileHandler(file_name, encoding="utf-8")
    file_handler.setLevel(LOG_LEVEL)
    file_handler.set_name(f"{file_name}")

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LONG_DATE_FORMAT)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger("sadx_linux_installer")
    logger.addHandler(file_handler)

    return logger

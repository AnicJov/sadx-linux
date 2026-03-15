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
from enum import Enum
from logging import DEBUG, ERROR, INFO, NOTSET, WARNING, Logger

from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL, LONG_DATE_FORMAT, SHORT_DATE_FORMAT

"""
Note:
    So I initially wrote a whole complicated logging system here but decided
    later that it was crap so I scrapped it and did the smart thing which is
    to use Python's logging module. Should have done that from the start (:

    The goal is to reuse this logging structure in other projects, which I'm
    already doing!
"""

class LogLevel(Enum):
    NOTSET  = NOTSET
    DEBUG   = DEBUG
    INFO    = INFO
    WARNING = WARNING
    ERROR   = ERROR


def get_logger():
    logging.setLoggerClass(Logger)
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt=LONG_DATE_FORMAT, force=True)
    file_name = str(LOG_FILE).replace(r"{ts_short}", time.strftime(SHORT_DATE_FORMAT))
    file_handler = logging.FileHandler(file_name, encoding="utf-8")
    file_handler.setLevel(LOG_LEVEL)
    file_handler.set_name(f"{file_name}")
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LONG_DATE_FORMAT)
    file_handler.setFormatter(formatter)
    logger = logging.getLogger("sadx_linux_installer")
    logger.addHandler(file_handler)

    return logger

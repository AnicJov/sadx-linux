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

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from contextvars import ContextVar
from functools import wraps
from typing import TypeVar, Any, cast
from util.logger import LogLevel


type LogCB = Callable[[LogLevel, str], None]
def _log_noop(_: LogLevel, __: str) -> None:
    pass
NOOP_LOG: LogCB = _log_noop

type ProgCB = Callable[[float], None]
def _noop_prog(_: float) -> None:
    pass
NOOP_PROG: ProgCB = _noop_prog

type CancCB = Callable[[], None]
def _noop_canc() -> None:
    return
NOOP_CANC: CancCB = _noop_canc

@dataclass(frozen=True, slots=True)
class Callbacks:
    prog: ProgCB = _noop_prog
    canc: CancCB = _noop_canc
    log:  LogCB  = _log_noop

"""
Black magic beyond this point
"""

_CBS: ContextVar[Callbacks] = ContextVar("callbacks", default=Callbacks())

def prog_cb(fraction: float) -> None:
    _CBS.get().prog(fraction)

def canc_cb() -> None:
    _CBS.get().canc()

def log_cb(level: LogLevel, msg: str) -> None:
    _CBS.get().log(level, msg)

R = TypeVar("R")

def callsback(func: Callable[..., R]) -> Callable[..., R]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        current = _CBS.get()

        prog_obj = kwargs.pop("prog_cb", current.prog)
        canc_obj = kwargs.pop("canc_cb", current.canc)
        log_obj  = kwargs.pop("log_cb",  current.log)

        if not callable(prog_obj):
            raise TypeError(f"prog_cb must be callable, got {type(prog_obj).__name__}")
        if not callable(canc_obj):
            raise TypeError(f"canc_cb must be callable, got {type(canc_obj).__name__}")
        if not callable(log_obj):
            raise TypeError(f"log_cb must be callable, got {type(log_obj).__name__}")

        prog = cast(ProgCB, prog_obj)
        canc = cast(CancCB, canc_obj)
        log  = cast(LogCB,  log_obj)

        token = _CBS.set(Callbacks(prog=prog, canc=canc, log=log))
        try:
            return func(*args, **kwargs)
        finally:
            _CBS.reset(token)

    return wrapper

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

import sys
from multiprocessing import set_start_method, freeze_support

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow
from src.util.fileio import resource_path
from util.qlogger import get_qlogger


def main(argc: int, argv: list[str]) -> int:
    # TODO: Implement CLI
    set_start_method("fork")  # For multiprocess work use fork instead of spawn
    freeze_support()
    app = QApplication(argv)
    app.setWindowIcon(QIcon(str(resource_path("icons/sonic.png"))))
    main_window = MainWindow(app, get_qlogger())
    main_window.show()
    return_code = app.exec()

    return return_code


if __name__ == "__main__":
    sys.exit(main(len(sys.argv), sys.argv))

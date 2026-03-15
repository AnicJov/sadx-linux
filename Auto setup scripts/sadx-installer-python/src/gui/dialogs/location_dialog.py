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

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QMessageBox,
    QLineEdit,
    QStyle,
)
from util.fileio import safe_makedirs
from config import BTN_SMALL_W, BTN_SMALL_H


class LocationDialog(QDialog):
    install_path = None

    def __init__(self, default_path: Path, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle('Choose install location')
        self.setModal(True)
        self.resize(600, 120)

        self.install_path = Path.home() / "Games" / "sadx"

        v = QVBoxLayout(self)
        h = QHBoxLayout()
        self.label = QLabel("<b>Please select the installation directory:</b>")
        self.path_edit = QLineEdit(str(default_path))
        self.path_edit.setFixedHeight(BTN_SMALL_H)
        self.browse = QPushButton('Browse...')
        if parent:
            style = parent.style()
        if style:
            self.browse.setIcon(style.standardIcon(getattr(QStyle.StandardPixmap, "SP_DirOpenIcon")))
        self.browse.setFixedSize(BTN_SMALL_W, BTN_SMALL_H)
        v.addWidget(self.label)
        h.addWidget(self.browse)
        h.addWidget(self.path_edit)
        v.addLayout(h)

        btns = QHBoxLayout()
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.setFixedSize(BTN_SMALL_W, BTN_SMALL_H)
        self.ok_btn = QPushButton('Continue')
        self.ok_btn.setFixedSize(BTN_SMALL_W, BTN_SMALL_H)
        btns.addStretch(1)
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.ok_btn)
        v.addLayout(btns)

        self.browse.clicked.connect(self.on_browse)
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.on_accept)
        self.path_edit.returnPressed.connect(self.on_accept)

    def selected_path(self) -> Path|None:
        if self.install_path is None:
            return None

        return self.install_path.expanduser().resolve()

    def on_browse(self) -> None:
        if self.install_path:
            browse_path = str(self.install_path)
        else:
            browse_path = str(Path.home())

        res = QFileDialog.getExistingDirectory(self, 'Select install directory', browse_path)
        if not res:
            return
        
        self.install_path = Path(res)

        if len(os.listdir(self.install_path)) != 0:
            self.install_path = self.install_path / 'sadx'

        self.path_edit.setText(self.install_path.expanduser().resolve().as_posix())

    def on_accept(self) -> None:
        self.install_path = Path(self.path_edit.text())

        if not self.install_path.as_posix():
            return

        if not Path.exists(self.install_path):
            dialog = QMessageBox()
            dialog.setWindowTitle("Directory doesn't exist")
            dialog.setText("The Selected directory does not exist. Do you want to create it?")
            dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            dialog.setDefaultButton(QMessageBox.StandardButton.Yes)
            if dialog.exec() == QMessageBox.StandardButton.Yes:
                safe_makedirs(self.install_path)
            else:
                return

        self.path_edit.setText(self.install_path.expanduser().resolve().as_posix())
        self.accept()

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

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QRadioButton,
)
from config import BTN_SMALL_H, BTN_SMALL_W


class VersionDialog(QDialog):
    version = "stable"

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle('Version Selection')
        self.setModal(True)
        self.resize(500, 200)

        h = QHBoxLayout()
        v = QVBoxLayout(self)

        label = QLabel("<b>Please select the version you want to install:</b>")

        # TODO: Add tooltips describing the options in more detail
        self.rb_stable = QRadioButton("Stable - New Mod Manager (Recommended)")
        self.rb_stable.setChecked(True)
        self.rb_legacy = QRadioButton("Legacy - Old Mod Manager")
        self.rb_unstable = QRadioButton("Unstable - Latest versions of everything")

        self.btn_continue = QPushButton("Continue")
        self.btn_continue.setFocus()
        self.btn_continue.setFixedSize(BTN_SMALL_W, BTN_SMALL_H)
        self.btn_continue.clicked.connect(self.on_continue)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedSize(BTN_SMALL_W, BTN_SMALL_H)
        self.btn_cancel.clicked.connect(self.reject)

        v.addWidget(label)
        v.addWidget(self.rb_stable)
        v.addWidget(self.rb_legacy)
        v.addWidget(self.rb_unstable)

        h.addStretch(1)
        h.addWidget(self.btn_cancel)
        h.addWidget(self.btn_continue)
        v.addLayout(h)

        self.setLayout(v)

    def selected_version(self) -> str:
        return self.version

    def on_continue(self) -> None:
        if self.rb_stable.isChecked():
            self.version = "stable"
        elif self.rb_legacy.isChecked():
            self.version = "legacy"
        elif self.rb_unstable.isChecked():
            self.version = "unstable"
        else:
            raise IndexError("No radio button was selected")

        self.accept()

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
    QCheckBox,
)
from config import BTN_SMALL_H, BTN_SMALL_W


class PostInstallDialog(QDialog):
    _selected_options = []

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle('Additional Actions')
        self.setModal(True)
        self.resize(500, 200)

        h = QHBoxLayout()
        v = QVBoxLayout(self)

        label = QLabel("<b>Would you like to do any of the following:</b>")

        self.cb_app_menu = QCheckBox("Create application menu entries")
        self.cb_app_menu.setChecked(True)
        self.cb_desktop = QCheckBox("Create desktop shortcuts")
        self.cb_desktop.setChecked(True)
        self.cb_rm_dl = QCheckBox("Clean up downloaded archives")
        self.cb_rm_dl.setChecked(True)

        style_sheet = """
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
            }
            QCheckBox {
                font-size: 14px;
            }
        """
        self.setStyleSheet(style_sheet)

        self.btn_continue = QPushButton("Continue")
        self.btn_continue.setFocus()
        self.btn_continue.setFixedSize(BTN_SMALL_W, BTN_SMALL_H)
        self.btn_continue.clicked.connect(self.on_continue)

        v.addWidget(label)
        v.addWidget(self.cb_app_menu)
        v.addWidget(self.cb_desktop)
        v.addWidget(self.cb_rm_dl)

        h.addStretch(1)
        h.addWidget(self.btn_continue)
        v.addLayout(h)

        self.setLayout(v)

    def selected_options(self) -> list[str]:
        return self._selected_options

    def on_continue(self) -> None:
        if self.cb_app_menu.isChecked():
            self._selected_options.append("menu")
        if self.cb_desktop.isChecked():
            self._selected_options.append("desktop")
        if self.cb_rm_dl.isChecked():
            self._selected_options.append("cleanup")

        self.accept()

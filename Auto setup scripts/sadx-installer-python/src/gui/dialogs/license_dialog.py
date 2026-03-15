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

from pathlib import Path
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QCheckBox,
    QPlainTextEdit,
    QMessageBox,
)
from config import BTN_SMALL_H, BTN_SMALL_W


class LicenseDialog(QDialog):
    def __init__(self, license_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('License and agreement')
        self.setModal(True)
        self.resize(575, 450)

        v = QVBoxLayout(self)
        label = QLabel(
            '<b>By using this installer you acknowledge and understand the following:</b>\n'
            '<ul>'
            '<li>The installer downloads and extracts ProtonGE, winetricks, the SADX coupon, and LiveSplit</li>'
            '<li>You will need <b>~3GiB</b> of free disk space to complete the install</li>'
            '<li>This software is distributed as-is with <b>no warrinty</b>. The author(s) are <b>not</b>'
            'liable for anything you do with this installer; any damages, including but not limited to, data loss</li>'
            '<li>This software is distributed under the GNU General Public License version 3:</li>'
            '</ul>'
        )
        label.setWordWrap(True)
        v.addWidget(label)

        scroll = QPlainTextEdit()
        scroll.setReadOnly(True)
        scroll.setFont(QFont('serif', 10))
        try:
            with open(license_path, 'r', encoding='utf-8') as f:
                scroll.setPlainText(f.read())
        except Exception:
            scroll.setPlainText('GPLv3 license file not found at: ' + str(license_path))
        v.addWidget(scroll)


        h = QHBoxLayout()
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.setFixedSize(BTN_SMALL_W, BTN_SMALL_H)
        self.ok_btn = QPushButton('Agree')
        self.ok_btn.setFixedSize(BTN_SMALL_W, BTN_SMALL_H)
        self.ok_btn.setFocus()
        self.agree_cb = QCheckBox('I understand and agree to proceed')
        self.agree_cb.setObjectName("agreeCB")
        self.agree_cb.setStyleSheet("""
            #agreeCB::indicator {
                width: 24px;
                height: 24px;
            }
            #agreeCB {
                font-size: 14px;
            }
        """)
        h.addWidget(self.agree_cb)
        h.addStretch(1)
        h.addWidget(self.cancel_btn)
        h.addWidget(self.ok_btn)
        v.addLayout(h)

        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.on_ok)

    def on_ok(self) -> None:
        if not self.agree_cb.isChecked():
            QMessageBox.warning(self, 'Agree', 'You must check the agreement box to proceed')
            return
        self.accept()

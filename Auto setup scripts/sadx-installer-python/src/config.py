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

from logging import DEBUG, ERROR, INFO, NOTSET, WARN
from pathlib import Path


# Versions
STABLE_VERSION: str = "1.0.0"
LEGACY_VERSION: str = "1.0.0"
PROTON_STABLE_VERSION:    str = "10-32"
LIVESPLIT_STABLE_VERSION: str = "1.8.37"

# Resource URLs
COUPON_LEGACY_URL:   str = (
    "aHR0cHM6Ly9kcml2ZS51c2VyY29udGVudC5nb29nbGUuY29tL2Rvd25sb2FkP2lkPTF6RmZL"
    "TkJ4NFpSMU9YXzhYcDJDc2RHbXZCZ2ZTd1lVcCZleHBvcnQ9ZG93bmxvYWQmYXV0aHVzZXI9"
    "MCZjb25maXJtPXQmdXVpZD02ODM1MTExYy0zOWY5LTQxOTktYTRmYi1mNThlMWU1MGZkYjc="
)
COUPON_STABLE_URL:   str = (
    "aHR0cHM6Ly9kcml2ZS51c2VyY29udGVudC5nb29nbGUuY29tL2Rvd25sb2FkP2lkPTFobVM5"
    "MlpqOGVpTVJfQWp4TjBZcU1PWEF0V1VjQlBoUyZleHBvcnQ9ZG93bmxvYWQmYXV0aHVzZXI9"
    "MCZjb25maXJtPXQmdXVpZD02ODM1MTExYy0zOWY5LTQxOTktYTRmYi1mNThlMWU1MGZkYjc="
)
COUPON_UNSTABLE_URL: str = (
    "aHR0cHM6Ly9kcml2ZS51c2VyY29udGVudC5nb29nbGUuY29tL2Rvd25sb2FkP2lkPTFobVM5"
    "MlpqOGVpTVJfQWp4TjBZcU1PWEF0V1VjQlBoUyZleHBvcnQ9ZG93bmxvYWQmYXV0aHVzZXI9"
    "MCZjb25maXJtPXQmdXVpZD02ODM1MTExYy0zOWY5LTQxOTktYTRmYi1mNThlMWU1MGZkYjc="
)
PROTON_LATEST_QURL:    str = "https://github.com/GloriousEggroll/proton-ge-custom/releases/latest/"
PROTON_LATEST_URL:    str = r"https://github.com/GloriousEggroll/proton-ge-custom/releases/download/{version}/{version}.tar.gz"
PROTON_STABLE_URL:    str = f"https://github.com/GloriousEggroll/proton-ge-custom/releases/download/GE-Proton{PROTON_STABLE_VERSION}/GE-Proton{PROTON_STABLE_VERSION}.tar.gz"
LIVESPLIT_LATEST_QURL: str = "https://github.com/LiveSplit/LiveSplit/releases/latest/"
LIVESPLIT_LATEST_URL: str = r"https://github.com/LiveSplit/LiveSplit/releases/download/{version}/LiveSplit_{version}.zip"
LIVESPLIT_STABLE_URL: str = f"https://github.com/LiveSplit/LiveSplit/releases/download/{LIVESPLIT_STABLE_VERSION}/LiveSplit_{LIVESPLIT_STABLE_VERSION}.zip"
COUPON_ZIP_PASSWORD:  str = "c2FkeGlzZnVubnk="

# Resource shecksums
COUPON_LEGACY_CHECKSUM:    str = "48f15e242566d226324167c21f226fafc22cc8cd"
COUPON_STABLE_CHECKSUM:    str = "d32fb929ff83975f37c452d693366b77d8ac0b1f"
COUPON_UNSTABLE_CHECKSUM:  str = "d32fb929ff83975f37c452d693366b77d8ac0b1f"
LIVESPLIT_STABLE_CHECKSUM: str = "a258f8146c8461e3ba6e62ec886f743c48b4373e"
PROTON_STABLE_CHECKSUM:    str = "9e0984280c01083d58ea0f76fc7fa6e6e9b5f2a2"

# Winetricks verbs to install
WINETRICKS_VERBS_BASE:     list[str] = ["wmp9", "gdiplus", "allfonts", "d3dx9", "quartz"]
WINETRICKS_VERBS_LEGACY:   list[str] = WINETRICKS_VERBS_BASE + ["dotnet45", "dotnet48"]
WINETRICKS_VERBS_STABLE:   list[str] = WINETRICKS_VERBS_BASE + ["dotnet48", "dotnet7", "dotnetdesktop7", "dotnet8", "dotnetdesktop8", "7zip"]
WINETRICKS_VERBS_UNSTABLE: list[str] = WINETRICKS_VERBS_BASE + ["dotnet48", "dotnet7", "dotnetdesktop7", "dotnet8", "dotnetdesktop8", "7zip"]

# UI Settings
BTN_SMALL_W: int = 120
BTN_SMALL_H: int =  30
BTN_BIG_W:   int = 160
BTN_BIG_H:   int =  40

# Installation steps
STEPS: list[tuple[str, int, str]] = [
#    <function to call>          <progress percentage>  <step description>
    ("create_dirs",                1,                   "Creating installation folders"),
    ("download_proton",            9,                   "Downloading Proton"),
    ("download_coupon",           14,                   "Downloading Coupon"),
    ("download_livesplit",         3,                   "Downloading LiveSplit"),
    ("extract_proton",             6,                   "Installing Proton"),
    ("create_wine_prefix",         4,                   "Creating Wine prefix"),
    ("extract_coupon",            20,                   "Installing game"),
    ("extract_livesplit",          2,                   "Installing LiveSplit"),
    ("ensure_winetricks_prereqs",  2,                   "Installing prerequisites"),
    ("winetricks_verbs_install",  36,                   "Installing Windows components"),
    ("set_dll_override",           2,                   "Configuring Wine prefix"),
    ("finalize",                   1,                   "Finalizing"),
]

# Logging settings
LOG_LEVEL                 = INFO
LOG_PROGRESS_AMOUNT: int  = 24
LOG_FORMAT:          str  = "[%(asctime)s] [%(levelname)s] %(message)s"
SHORT_DATE_FORMAT:   str  = "%y%m%dT%H%M%S"
LONG_DATE_FORMAT:    str  = "%Y-%m-%d %H:%M:%S"
LOG_FILE:            Path = Path.home() / ".local" / "share" / "sadx-installer" / "logs" / "sadx_installer_{ts_short}.log"

# Location settings
DEFAULT_INSTALL_PATH: Path = Path.home() / "Games" / "sadx"
COMPAT_PATH:          Path = Path(".compat")
DOWNLOADS_PATH:       Path = Path(".downloads")
TOOLS_PATH:           Path = Path("Tools")
PREFIX_PATH:          Path = COMPAT_PATH / "pfx"
LAUNCHERS_PATH:       Path = COMPAT_PATH / "launchers"
RESOURCES_PATH:       Path = COMPAT_PATH / "res"
PROTON_PATH:          Path = COMPAT_PATH / "proton"
ICON_SADX:            Path = RESOURCES_PATH / "sonic.png"
ICON_LIVESPLIT:       Path = RESOURCES_PATH / "livesplit.png"
LICENSE_PATH:         Path = RESOURCES_PATH / "LICENSE"
SADX_PATH:            Path = PREFIX_PATH / "drive_c" / "Program Files" / "SONICADVENTUREDX"

# Dev settings
DEV_RES_PATH:         Path = Path.cwd() / "res"
ASSUME_EXTRACTED:     bool = False

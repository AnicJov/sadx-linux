# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_root = Path(SPECPATH).resolve()
src_root = project_root / "src"

def collect_tree(src: Path, dest_root: str):
    datas = []
    if not src.exists():
        return datas

    for path in src.rglob("*"):
        if path.is_file():
            rel_parent = path.parent.relative_to(src)
            target_dir = str(Path(dest_root) / rel_parent)
            datas.append((str(path), target_dir))
    return datas

datas = []
datas += collect_tree(project_root / "res", "res")

for extra_file in [
    project_root / "LICENSE",
    project_root / "livesplit-livesplit.xml",
    project_root / "Codaxy.Xlio.dll",
    project_root / "AUTHORS.txt",
    project_root / "README.md",
]:
    if extra_file.exists():
        datas.append((str(extra_file), "."))

hiddenimports = []
hiddenimports += collect_submodules("PyQt6")

a = Analysis(
    [str(src_root / "main.py")],
    pathex=[str(project_root), str(src_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "unittest",
        "test",
        "pytest",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="sadx-installer",
    icon=str(project_root / "res" / "icons" / "sonic.png"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="sadx-installer",
)

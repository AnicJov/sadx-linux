# Automatic SADX installer for speedrunning on Linux

PyQt6 GUI installer for SADX intended for speedrunning on Linux distributions.
Install prerequisites (Prerequisites section below), choose your preferred installation method (Usage section below) and follow the installation process.

Note:
  Documentation and code are not quite finished yet.

# Prerequisites

For installing and running the game and LiveSplit you will need some system packages installed, as shown below.

### Arch / Manjaro / CachyOS
```sh
sudo pacman -Syu --needed --noconfirm steam cabextract unzip wget perl fontconfig freetype2 lib32-glibc lib32-gcc-libs lib32-fontconfig lib32-freetype2
```

### Debian / Ubuntu / Mint
Note:
  Untested
```sh
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install -y steam cabextract unzip wget perl libfontconfig1 libfreetype6 libc6:i386 libfontconfig1:i386 libfreetype6:i386
```

### Fedora / CentOS / RHEL
Note:
  Untested
```sh
sudo dnf install -y steam cabextract unzip wget which gzip fontconfig freetype glibc.i686 fontconfig.i686 freetype.i686
```

### OpenSUSE (Tumbleweed/Leap)
Note:
  Untested
```sh
sudo zypper install -y steam cabextract unzip wget perl fontconfig glibc-32bit libfontconfig1-32bit libfreetype6 libfreetype6-32bit
```


# Usage

### Running from binary release
- Download the archive from the [releases page](https://github.com/AnicJov/sadx-linux/releases/latest)
- Extract the archive (e.g. `tar -xvf sadx-installer.tar.gz`)
- Run the binary (e.g. double click if allowed on distro, or `./sadx-installer`)

### Running from source
```sh
git clone https://github.com/AnicJov/sadx-linux.git
cd "sadx-linux/Auto setup scripts/sadx-installer-python"

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the script
python src/main.py
```

### Building binary
```sh
git clone https://github.com/AnicJov/sadx-linux.git
cd "sadx-linux/Auto setup scripts/sadx-installer-python"

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pyinstaller --clean --noconfirm sadx-installer.spec

# Run the binary
dist/sadx-installer

# Optional: create a tarball
cd dist && tar -cvf sadx-installer.tar.gz sadx-installer
```


# Help & Contributing

Any feedback, issue reports or PRs are welcome. You can reach me mainly through this repository and Discord (`_anic`), feel free to reach out.


# Credits & Legal

- AnicJov - SADX installer (GPLv3)
- Nanami, Labrys - SADX installer testing

- Stuart Caie - cabextract (GPL)
- WineHQ - wine (LGPL)
- Valve - proton (BSD)
- Austin English - winetricks (GPLv2.1)

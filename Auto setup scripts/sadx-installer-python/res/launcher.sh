#!/bin/sh

export WINEPREFIX="{prefix}"
export WINEDEBUG="fixme-all"
export STEAM_COMPAT_DATA_PATH="{compat}"
export STEAM_COMPAT_CLIENT_INSTALL_PATH="{compat}"
export PROTONFIXES_DISABLE="1"

cd "{exe_dir}"
exec {run_cmd} "{exe_path}" "$@"

#!/bin/sh

export WINEPREFIX="{prefix}"
export WINEDEBUG="fixme-all"
export STEAM_COMPAT_DATA_PATH="{compat}"
export STEAM_COMPAT_CLIENT_INSTALL_PATH="{compat}"
export PROTONFIXES_DISABLE="1"

# Select the display driver for the current desktop session.
case "$XDG_SESSION_TYPE" in
    wayland) PROTON_ENABLE_WAYLAND=1 ;;
    x11) PROTON_ENABLE_WAYLAND=0 ;;
    *)
        if [ -n "$WAYLAND_DISPLAY" ]; then
            PROTON_ENABLE_WAYLAND=1
        else
            PROTON_ENABLE_WAYLAND=0
        fi
        ;;
esac
export PROTON_ENABLE_WAYLAND
export PROTON_USE_WAYLAND="$PROTON_ENABLE_WAYLAND"

cd "{exe_dir}"
exec {run_cmd} "{exe_path}" "$@"

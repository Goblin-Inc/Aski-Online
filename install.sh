#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
if command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --needed python python-pyqt6 python-requests
elif command -v apt >/dev/null 2>&1; then
    sudo apt update && sudo apt install -y python3 python3-pyqt6 python3-requests
fi
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications"
ln -sf "$DIR/run.sh" "$HOME/.local/bin/aski-online"
cat << DESKTOP > "$HOME/.local/share/applications/aski-online.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Aski Online
GenericName=Retro AI Messenger
Comment=2000s Retro ICQ/XP Style AI Messenger
Exec=$DIR/run.sh
Icon=aski-online
Terminal=false
Categories=Network;InstantMessaging;Chat;
DESKTOP
chmod +x "$HOME/.local/share/applications/aski-online.desktop"
echo "Готово! Запускайте: ./run.sh или aski-online"

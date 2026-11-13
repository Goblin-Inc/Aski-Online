#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
if command -v pacman >/dev/null 2>&1; then
    sudo pacman -S --needed python python-pyqt6 python-requests
elif command -v apt >/dev/null 2>&1; then
    sudo apt update && sudo apt install -y python3 python3-pyqt6 python3-requests
fi
mkdir -p "$HOME/.local/bin"
cat << RUN > "$HOME/.local/bin/aski-online"
#!/usr/bin/env bash
cd "$DIR"
exec python3 "$DIR/main.py" "\$@"
RUN
chmod +x "$HOME/.local/bin/aski-online"
echo "Готово! Запускайте: python3 main.py или aski-online"

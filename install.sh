
#!/data/data/com.termux/files/usr/bin/bash

set -eu

APP_NAME="White Bird"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

RED='\033[0;31m'
WHITE='\033[1;37m'
RESET='\033[0m'

echo -e "${RED}========================================${RESET}"
echo -e "${WHITE}       WHITE BIRD INSTALLER v2.8${RESET}"
echo -e "${RED}       Developer: Firewall-Crusher${RESET}"
echo -e "${RED}========================================${RESET}"

if ! command -v pkg >/dev/null 2>&1; then
    echo "Error: This installer requires Termux."
    exit 1
fi

echo "[1/3] Installing required packages..."
pkg install -y python nano

echo "[2/3] Checking application files..."
if [ ! -f "$SCRIPT_DIR/white_bird.py" ]; then
    echo "Error: white_bird.py was not found."
    echo "Place install.sh beside white_bird.py and try again."
    exit 1
fi

chmod +x "$SCRIPT_DIR/white_bird.py"

echo "[3/3] Installation complete."
echo
echo "Start White Bird with:"
echo "cd \"$SCRIPT_DIR\""
echo "python white_bird.py"
echo
echo "Developer: Firewall-Crusher"
echo "Profile: https://codeberg.org/Firewall-Crusher"
echo -e "${RED}========================================${RESET}"

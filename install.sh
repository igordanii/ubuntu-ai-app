#!/usr/bin/env bash

# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-dev python3-venv python3-pip python3-gi python3-gi-cairo gir1.2-gtk-3.0 libgtk-3-dev tesseract-ocr tesseract-ocr-eng tesseract-ocr-por gnome-screenshot scrot xclip

# Create and activate virtual environment
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Change to the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Install Python dependencies
pip install -r requirements.txt

# Configure keyboard shortcut with virtual environment's Python
APP_PATH="$SCRIPT_DIR/main_app_launcher.py"
KEYBINDING="<Ctrl><Shift>A"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3" # Path to venv's Python

gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/']"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ name 'Screenshot Tool'
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ command "$VENV_PYTHON $APP_PATH"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ binding "$KEYBINDING"

echo "Dependencies installed and keyboard shortcut configured!"

echo "Dependencies installed!"
# Ubuntu AI Screenshot Enhancer 🚀  
**Project Status: Alpha / Work in Progress 🚧 – May 26, 2025**

This application enhances your screenshot workflow on Ubuntu by integrating powerful AI capabilities directly into your captures using Google's Gemini API. Take screenshots, then instantly extract text, translate it, or copy it to your clipboard.

---

## Key Features

- 🖼️ **Flexible Capture**: Choose between capturing the full screen or selecting a specific area. An initial dialog allows easy mode selection via mouse click or keyboard shortcuts (`1` for area, `2` for full screen).
- ✨ **Instant Overlay UI**: After a screenshot is taken, a sleek, temporary preview window appears with icon-based actions:
  - 👁️ **Recognize & Extract Text**: Uses Tesseract OCR to pull text directly from the captured image.
  - 🌐 **AI-Powered Translation**: Translate the extracted image text into various languages (selected via a dialog) using the Gemini API.
  - 📋 **Quick Copy**: Easily copy the extracted text to your clipboard.
  - 💾 **Save Image**: Save the screenshot to your default directory (`~/Pictures/Screenshots/`).
- ⌨️ **Keyboard Shortcut Launch**: Designed to be launched via a global system keyboard shortcut for quick access.
- 🚪 **Clean Exit**: The application and its preview window close properly when actions are completed or dismissed.

---

## Core Technologies

- **Language**: Python 3  
- **GUI**: GTK+ 3 (via PyGObject) for a native Ubuntu look and feel  
- **AI Language Model**: Google Gemini API (for text translation)  
- **OCR Engine**: Tesseract OCR  
- **Clipboard Integration**: Pyperclip  
- **System Screenshot Tools**: `gnome-screenshot` (for Wayland/GNOME) and `scrot` (for X11)

---

## Installation

### 1. System Dependencies (Install via APT)

Open your terminal and run the following commands:

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    libgtk-3-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-por \
    gnome-screenshot \
    scrot \
    xclip
````

* `tesseract-ocr-por`: Included as an example for Portuguese OCR. Add or replace with other language packs as needed (e.g., `tesseract-ocr-spa` for Spanish).
* You can search for available packs with:

  ```bash
  apt search tesseract-ocr-
  ```
* `xclip`: Used by pyperclip for clipboard access on Linux. `xsel` is an alternative.

---

### 2. Clone the Repository (Recommended)

If you are managing this project with Git, clone it:

```bash
git clone <your-repository-url>
cd <screenshot-enhancer-repository-name>
```

Otherwise, ensure all project files for the screenshot enhancer (e.g., `main_app_launcher.py`, `capture_mode_dialog.py`, `capture_utils.py`, `display_window.py`, `ocr_utils.py`, `gemini_utils.py`, `common_dialogs.py`) are in the same main project directory.

---

### 3. Set Up Python Virtual Environment

```bash
# Ensure you are in the project's root directory
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

> The `--system-site-packages` flag is crucial for PyGObject to interface with system-installed GTK libraries.

---

### 4. Install Python Dependencies

Create a `requirements.txt` file in your project’s root directory. A minimal version might include:

```txt
# For image manipulation in OCR
Pillow
# Python wrapper for Tesseract OCR
pytesseract
# Google Gemini API client library
google-generativeai
# For loading environment variables (like API keys from .env file)
python-dotenv
# For cross-platform clipboard access
pyperclip
```

Then install the packages:

```bash
# Ensure your virtual environment (venv) is active
pip install -r requirements.txt
```

To generate `requirements.txt` from your current working environment:

```bash
pip freeze > requirements.txt
```

---

## Configuration

### Google Gemini API Key (for Translation)

The translation feature uses the Google Gemini API. You need an API key from [Google AI Studio](https://makersuite.google.com/).

1. Create a `.env` file in the root directory of the project.
2. Add your API key to the `.env` file:

```env
GOOGLE_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"
```

3. Ensure `.env` is in your `.gitignore` file.

---

## Usage

1. **Activate the virtual environment**:

```bash
source venv/bin/activate
```

2. **Launch the Application**:

```bash
python3 main_app_launcher.py
```

> Recommended: Configure this command to run via a **global system keyboard shortcut** for easy access (see "Known Issues / Challenges").

3. **Select Capture Mode**:
   An initial dialog will prompt you to choose:

   * "Select Area" (press `1`)
   * "Full Screen" (press `2`)

4. **Take Screenshot**:
   Perform the capture as prompted.

5. **Use Action Buttons**:
   The screenshot preview window will appear with icon buttons:

   * **Save**: Saves the image to `~/Pictures/Screenshots/`.
   * **Translate**: Extracts text, shows a language selection dialog, then translates using Gemini API.
   * **Copy Text**: Extracts text and copies it to the clipboard.
   * **Close**: Closes the preview window and the application (or press `Esc`).

---

## Current Status (as of May 26, 2025)

**Alpha / Work in Progress 🚧**

* ✅ Core screenshot capture logic (full screen, area selection) via system tools is functional.
* ✅ Initial dialog for capture mode selection (icon buttons, keyboard `1`/`2`) is implemented.
* ✅ Temporary screenshot display window with GTK+3, featuring icon-based buttons (Save, Translate, Copy, Close) is operational.
* ✅ "Save Image", "Copy Text" (OCR + Clipboard), and "Translate Text" (OCR + Language Selection Dialog + Gemini API) functionalities are implemented.
* ✅ Application closes cleanly when the preview window is dismissed.

---

## Known Issues / Challenges

* **Global Keyboard Shortcut Configuration**:
  Launching the application via a global hotkey requires manual configuration in Ubuntu’s system settings:

  * Go to: `Settings -> Keyboard -> Keyboard Shortcuts -> Custom Shortcuts`
  * Use the full path to the Python interpreter in your venv followed by the full path to your main script (e.g., `main_app_launcher.py`)
  * Ensure the working directory and environment are correctly set (the script attempts to `os.chdir` to its own directory).

* **Deprecation Warnings**:
  Some GDK functions used for screen/pointer information (e.g., `Gdk.Screen.get_number`) may show deprecation warnings in the console. These should be updated to their modern equivalents in future versions.

```

Let me know if you'd like this turned into an actual file (`README.md`) or tailored to a specific style (e.g., more minimal, dark theme previews, emojis removed, etc.).
```

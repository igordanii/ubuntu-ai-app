Okay, here is the content for your `README.md` file, provided directly in this chat:

```markdown
# Ubuntu AI Productivity Suite 🚀

**(Project Status: Alpha / Work in Progress 🚧 - May 2025)**

This project is building a versatile AI assistant integrated into the Ubuntu desktop, designed to streamline common tasks involving screenshots and text manipulation through the power of Google's Gemini API.

The suite aims to provide two main components:

**1. Smart Screenshot Enhancer:**
Transform your static screenshots into interactive content.

* 🖼️ **Flexible Capture:** Full screen or select a specific area using native system tools.
* ✨ **Instant Overlay UI:** After capture, a sleek, temporary window appears with icon-based actions:
    * 👁️ **Recognize & Extract Text:** Uses Tesseract OCR to pull text directly from the image.
    * 🌐 **AI-Powered Translation (Image Text):** Translate the extracted text using the Gemini API (e.g., to Brazilian Portuguese or other configured languages).
    * 📋 **Quick Copy (Image Text):** Easily copy the extracted text to your clipboard.
    * 💾 **Save Image:** Save the screenshot to your preferred directory (`~/Pictures/Screenshots/` by default).

**2. System-Wide AI Text Assistant (Planned & In Development):**
Access AI capabilities anywhere you can select text.

* 🔍 **Contextual Text Actions:** Upon selecting text in any application, a discreet UI (to be designed) will offer:
    * 🌍 **Instant Translation (Selected Text):** Translate selected text to your desired language via Gemini API.
    * ✍️ **AI Summarization:** Get quick summaries of lengthy selected passages using Gemini API.
    * 💅 **Format Improvement:** Let AI help reformat or improve the clarity of selected text using Gemini API.

---

## Core Technologies

* **Language:** Python 3
* **GUI:** GTK+ 3 (via PyGObject) for a native Ubuntu look and feel.
* **AI Language Model:** Google Gemini API
* **OCR Engine:** Tesseract OCR
* **Clipboard Integration:** Pyperclip
* **System Interaction:** Native Linux tools (`gnome-screenshot`, `scrot`) and libraries for screenshotting and potentially text selection monitoring.

---

## Installation

Follow these steps to set up the Ubuntu AI Productivity Suite on your system.

**1. System Dependencies (Install via APT):**

Open your terminal and run the following commands to install the necessary system-level packages:

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
```

* **`tesseract-ocr-por`**: Included for Portuguese OCR. Add or replace with other language packs as needed (e.g., `tesseract-ocr-spa` for Spanish, `tesseract-ocr-fra` for French). You can search for available Tesseract language packs with `apt search tesseract-ocr-`.
* **`xclip`**: Used by `pyperclip` for clipboard access on Linux. `xsel` is an alternative if `xclip` is not preferred.

**2. Clone the Repository (Recommended):**

If you are managing this project with Git, clone it:

```bash
git clone <your-repository-url>
cd <repository-name> # e.g., cd ubuntu-ai-suite
```
If you don't have a repository yet, simply ensure all project files (`main_app.py`, `capture_utils.py`, `display_window.py`, `ocr_utils.py`, `gemini_utils.py`, etc.) are in the same main project directory.

**3. Set Up Python Virtual Environment:**

Using a Python virtual environment is strongly recommended to manage dependencies.

```bash
# Ensure you are in the project's root directory
python3 -m venv --system-site-packages venv
source venv/bin/activate
```
* The `--system-site-packages` flag is crucial for PyGObject (GTK bindings) to correctly interface with the system-installed GTK libraries.

**4. Install Python Dependencies:**

Create a `requirements.txt` file in your project's root directory. This file should list all Python packages your project depends on.

A minimal `requirements.txt` would look something like this:
```txt
# For image manipulation in OCR and creating dummy images for testing
Pillow

# Python wrapper for Tesseract OCR
pytesseract

# Google Gemini API client library
google-generativeai

# For loading environment variables (like API keys from .env file)
python-dotenv

# For cross-platform clipboard access
pyperclip

# For monitoring file system events (if you implement screenshot directory monitoring)
# watchdog
```

Once `requirements.txt` is created and populated, install the packages:
```bash
# Ensure your virtual environment (venv) is active
pip install -r requirements.txt
```
*To generate `requirements.txt` from your current working environment (after installing packages manually with pip): `pip freeze > requirements.txt`*

---

## Configuration

**Google Gemini API Key:**

This application uses the Google Gemini API. You need to obtain an API key:
1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Create or use an existing API key.

To configure your API key securely for this application:

1.  In the root directory of the project, create a file named `.env`.
2.  Add your API key to this `.env` file in the following format:

    ```env
    GOOGLE_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"
    ```

3.  The application uses the `python-dotenv` library (listed in `requirements.txt`) to load this key from the `.env` file.
4.  **Important:** Add `.env` to your `.gitignore` file to prevent your API key from being accidentally committed to version control.

---

## Usage

1.  **Activate the virtual environment** (if not already active):
    ```bash
    source venv/bin/activate
    ```
2.  **Run the main application script** from the project's root directory:
    ```bash
    python3 main_app.py
    ```

**Screenshot Workflow:**
* Launch the application. It will typically present an option to take a full-screen or area-selection screenshot.
* After the screenshot is captured, a temporary preview window will appear.
* **Save Icon:** Saves the current screenshot to `~/Pictures/Screenshots/` (by default).
* **Translate Icon:** Extracts text from the screenshot using OCR and then translates it using the Gemini API. The result is shown in a dialog.
* **Copy Text Icon:** Extracts text from the screenshot using OCR and copies it to the system clipboard.
* **Close Icon (or pressing the `Esc` key):** Closes the preview window. If the image was a temporary capture, the temporary file is deleted.

**System-Wide Text Assistant (Planned):**
* (Detailed usage instructions for this feature will be added as it becomes available.)

---

## Current Status (as of May 2025)

* **Alpha / Work in Progress 🚧**
* Core screenshot capture functionality (using `gnome-screenshot` for Wayland/GNOME, `scrot` for X11) is implemented.
* Temporary screenshot display window with GTK+3, featuring icon-based buttons, is operational.
* "Save Image" button functionality is complete.
* "Copy Text" (OCR + Clipboard) and "Translate Text" (OCR + Gemini API) from screenshots are partially implemented (UI connected, core logic integration in progress).
* System-wide text selection monitoring and associated AI actions (translate, summarize, format) are in the planning and early design stages.

---

## Contributing

This project is currently under active development. If you're interested in contributing in the future, please check back for guidelines on reporting issues, suggesting features, or submitting pull requests.

(Placeholder: Specific contribution guidelines will be added if the project opens up for broader collaboration.)

---

## License

(Specify your chosen open-source license here. For example: "This project is licensed under the MIT License - see the LICENSE.md file for details.")

```
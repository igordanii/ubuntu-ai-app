# Ubuntu AI Productivity Suite 🚀

**(Project Status: Alpha / Work in Progress 🚧 - May 2025)**

This project is building a versatile AI assistant integrated into the Ubuntu desktop, designed to streamline common tasks involving screenshots and text manipulation through the power of Google's Gemini API.

The suite aims to provide two main components:

**1. Smart Screenshot Enhancer:**
Transform your static screenshots into interactive content.

* 🖼️ **Flexible Capture:** Full screen or select a specific area using native system tools, triggered by a keyboard shortcut. An initial dialog allows choosing the capture mode.
* ✨ **Instant Overlay UI:** After capture, a sleek, temporary window appears with icon-based actions:
    * 👁️ **Recognize & Extract Text:** Uses Tesseract OCR to pull text directly from the image.
    * 🌐 **AI-Powered Translation (Image Text):** Translate the extracted text using the Gemini API, with a language selection dialog.
    * 📋 **Quick Copy (Image Text):** Easily copy the extracted text to your clipboard.
    * 💾 **Save Image:** Save the screenshot to your preferred directory (`~/Pictures/Screenshots/` by default).
* 🚪 **Clean Exit:** Application closes properly when the screenshot window is dismissed (via Esc or Close button).

**2. System-Wide AI Text Assistant (In Development):**
Access AI capabilities for any text you copy to the clipboard.

* 📋 **Clipboard Monitoring:** Actively monitors the system clipboard for new text copied by the user (e.g., via Ctrl+C).
* ✨ **Floating Action Panel:** When new text is copied, a small, undecorated panel with icon buttons appears near the mouse cursor, offering:
    * 🌍 **Instant Translation (Selected Text):** Translate copied text to your desired language (selected via dialog) using Gemini API.
    * ✍️ **AI Summarization:** Get quick summaries of copied passages using Gemini API.
    * 💅 **Format Improvement:** Let AI help reformat or improve the clarity of copied text using Gemini API.
* 🖱️ **Contextual & Transient UI:** The floating panel is designed to appear on new text copy and hide when focus is lost, Esc is pressed, or an action is taken.

---

## Core Technologies

* **Language:** Python 3
* **GUI:** GTK+ 3 (via PyGObject) for a native Ubuntu look and feel.
* **AI Language Model:** Google Gemini API
* **OCR Engine:** Tesseract OCR
* **Clipboard Integration:** Pyperclip (for screenshot part), `wl-paste` (for system-wide text assistant on Wayland).
* **System Interaction:** Native Linux tools (`gnome-screenshot`, `scrot`, `wl-paste`) and libraries.

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
    xclip \
    wl-clipboard
tesseract-ocr-por: Included for Portuguese OCR. Add or replace with other language packs as needed (e.g., tesseract-ocr-spa for Spanish, tesseract-ocr-fra for French). You can search for available Tesseract language packs with apt search tesseract-ocr-.xclip: Used by pyperclip (primarily for the screenshot component's copy action). xsel is an alternative.wl-clipboard: Provides wl-paste, which is used by the system-wide text assistant for clipboard access on Wayland.2. Clone the Repository (Recommended):If you are managing this project with Git, clone it:git clone <your-repository-url>
cd <repository-name> # e.g., cd ubuntu-ai-suite
If you don't have a repository yet, simply ensure all project files (main_app_launcher.py, text_assistant_main.py, capture_utils.py, display_window.py, floating_action_panel.py, ocr_utils.py, gemini_utils.py, common_dialogs.py, text_action_dialogs.py) are in the same main project directory.3. Set Up Python Virtual Environment:Using a Python virtual environment is strongly recommended to manage dependencies.# Ensure you are in the project's root directory
python3 -m venv --system-site-packages venv
source venv/bin/activate
The --system-site-packages flag is crucial for PyGObject (GTK bindings) to correctly interface with the system-installed GTK libraries.4. Install Python Dependencies:Create a requirements.txt file in your project's root directory. This file should list all Python packages your project depends on.A minimal requirements.txt would look something like this:# For image manipulation in OCR and creating dummy images for testing
Pillow
# Python wrapper for Tesseract OCR
pytesseract
# Google Gemini API client library
google-generativeai
# For loading environment variables (like API keys from .env file)
python-dotenv
# For cross-platform clipboard access (used in screenshot module)
pyperclip
Once requirements.txt is created and populated, install the packages:# Ensure your virtual environment (venv) is active
pip install -r requirements.txt
To generate requirements.txt from your current working environment (after installing packages manually with pip): pip freeze > requirements.txtConfigurationGoogle Gemini API Key:This application uses the Google Gemini API. You need to obtain an API key:Go to Google AI Studio.Create or use an existing API key.To configure your API key securely for this application:In the root directory of the project, create a file named .env.Add your API key to this .env file in the following format:GOOGLE_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"
The application uses the python-dotenv library (listed in requirements.txt) to load this key from the .env file.Important: Add .env to your .gitignore file to prevent your API key from being accidentally committed to version control.UsageActivate the virtual environment (if not already active):source venv/bin/activate
Screenshot Enhancer:Run: python3 main_app_launcher.py (or your main script for screenshots).This should ideally be configured to run via a system-wide keyboard shortcut (see "Known Issues / Challenges" for setting this up).An initial dialog will ask for capture mode (Area/Full Screen).After capture, the preview window with action buttons appears.System-Wide Text Assistant:Run: python3 text_assistant_main.pyThis runs in the background, monitoring clipboard "Copy" events.When you copy text (Ctrl+C) in any application, the floating action panel should appear near your mouse.Click an icon on the panel to perform an action.To stop the assistant, press Ctrl+C in the terminal where it's running.Current Status (as of May 14, 2025)Alpha / Work in Progress 🚧Screenshot Enhancer:Core capture logic (full screen, area selection) via system tools is functional.Initial dialog for capture mode selection (icon buttons, keyboard '1'/'2') implemented.Temporary screenshot display window with GTK+3, featuring icon-based buttons (Save, Translate, Copy, Close) is operational."Save Image," "Copy Text" (OCR + Clipboard), and "Translate Text" (OCR + Language Selection Dialog + Gemini API) functionalities are implemented for screenshots.System-Wide Text Assistant:Background process monitors clipboard "Copy" events using wl-paste (for Wayland).Floating action panel UI (undecorated, icon buttons) appears on new text copy.Actions (Translate with language selection, Summarize, Improve Format) using Gemini API are connected.Result display dialogs are functional.Known Issues / ChallengesFloating Panel Stability (System-Wide Text Assistant):The floating action panel currently exhibits a "flickering" behavior on Wayland: it appears when text is copied but may immediately hide due to focus management complexities with undecorated top-level windows.Reliably keeping the panel visible and interactive without it stealing focus inappropriately, or disappearing too soon, is an ongoing challenge.The panel's position is based on mouse cursor coordinates; if these are reported as (0,0) (which sometimes happens initially on Wayland), a fallback attempts to center it, but precise positioning near selected text needs improvement.Global Keyboard Shortcut for Screenshot Tool:The screenshot part of the application (main_app_launcher.py) needs to be manually configured in Ubuntu's system settings (Settings -> Keyboard -> Keyboard Shortcuts -> Custom Shortcuts) to be launched via a global hotkey. The command would be something like:/full/path/to/your/project/venv/bin/python3 /full/path/to/your/project/main_app_launcher.pyEnsuring the correct working directory and environment for scripts launched this way is important.Wayland PRIMARY Selection:The original goal of reacting to any highlighted text (PRIMARY selection) for the system-wide assistant is very difficult on Wayland due to security restrictions. The current implementation relies on explicit "Copy" actions (CLIPBOARD selection). AT-SPI might be a future avenue for PRIMARY selection but is significantly more complex.wl-paste Timeouts: Occasional timeouts from wl-paste can cause the text assistant to miss a clipboard update or briefly think the clipboard is empty. The current logic tries to use the last known good text in such cases.Contributing to Ubuntu AI Productivity SuiteWe welcome contributions to the Ubuntu AI Productivity Suite! Whether you're reporting a bug, suggesting an enhancement, or writing code, your help is appreciated. Here's how you can contribute:1. Reporting BugsCheck Existing Issues: Before submitting a new bug report, please check the GitHub Issues to see if the bug has already been reported.Provide Details: If you're submitting a new bug, please include as much detail as possible:A clear and descriptive title.Steps to reproduce the bug.What you expected to happen.What actually happened (including any error messages and full console output).Your Ubuntu version, desktop environment (e.g., GNOME, XFCE), and whether you're using X11 or Wayland (echo $XDG_SESSION_TYPE).The version of the application you are using (if applicable, e.g., a Git commit hash or branch name).2. Suggesting Enhancements or New FeaturesCheck Existing Issues/Discussions: Your idea might already be under discussion. Check the GitHub Issues (look for "enhancement" or "feature request" labels) or GitHub Discussions (if you enable this feature).Be Clear and Specific:Provide a clear and descriptive title for your suggestion.Explain the enhancement or feature in detail. What would it do? Why is it useful?Provide examples or mockups if possible.3. Code Contributions (Pull Requests)We are happy to accept code contributions! Please follow these steps:Fork the Repository: Create your own fork of the project on GitHub.Clone Your Fork:git clone [https://github.com/](https://github.com/)<your-github-username>/<repository-name>.git
cd <repository-name>
Set Up Development Environment: Follow the Installation instructions.Create a New Branch: Use a descriptive name (e.g., feat/improve-panel-focus or fix/wl-paste-timeout-handling).git checkout -b name-of-your-new-branch
Make Your Changes:Write clean, well-commented code (PEP 8 for Python).Ensure your changes do not break existing functionality.Update documentation (like this README) if your changes affect usage or setup.Commit Your Changes: Write clear commit messages.Push to Your Fork:git push origin name-of-your-new-branch
Open a Pull Request (PR):Provide a clear title and description, linking to any relevant issues.Be prepared for feedback and code review.4. Coding Style (Python)Please follow PEP 8 -- Style Guide for Python Code.Use clear variable and function names.Add comments to explain complex logic.5. Questions?If you have any questions about contributing, feel free to open an issue on GitHub.
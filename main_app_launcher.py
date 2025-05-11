# main_app_launcher.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os
import sys
import time # For any debugging delays if needed

# Ensure the script's directory is the current working directory
# This helps with relative imports and finding utility files.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)
print(f"MAIN_APP: Changed CWD to: {APP_DIR}")

# Import your project modules
from capture_utils import capture_screen
from display_window import show_screenshot # This is your ScreenshotDisplayWindow logic
from capture_mode_dialog import CaptureModeSelectionDialog # The new dialog

def run_main_application_flow(capture_mode_is_full_screen):
    """
    Handles the main flow after capture mode is selected:
    1. Takes screenshot.
    2. Shows display window with buttons.
    """
    print(f"MAIN_APP: Proceeding with capture. Full screen: {capture_mode_is_full_screen}")
    temp_image_path = capture_screen(full_screen=capture_mode_is_full_screen)

    if temp_image_path:
        print(f"MAIN_APP: Screenshot captured: {temp_image_path}")
        # The show_screenshot function from display_window.py handles its own window
        # and ScreenshotDisplayWindow's on_destroy calls Gtk.main_quit()
        show_screenshot(temp_image_path, is_temporary_file=True)
        # Gtk.main() will be started after this function returns, or if already running,
        # this new window will join the existing loop.
    else:
        print("MAIN_APP: Screenshot capture failed or was cancelled. Exiting application.")
        Gtk.main_quit() # Quit if capture fails early

if __name__ == "__main__":
    print("MAIN_APP: Application starting...")

    # 1. Show the capture mode selection dialog first
    mode_dialog = CaptureModeSelectionDialog()
    response = mode_dialog.run() # This blocks until the dialog emits a response

    chosen_mode = None
    if response == Gtk.ResponseType.OK:
        chosen_mode = mode_dialog.get_selected_mode()
        print(f"MAIN_APP: Mode selected from dialog: {chosen_mode}")
    else:
        print("MAIN_APP: Capture mode selection cancelled or dialog closed. Exiting.")
        mode_dialog.destroy()
        sys.exit(0) # Exit cleanly if no mode is chosen

    mode_dialog.destroy() # Important to destroy the dialog

    # 2. Proceed based on selection
    if chosen_mode:
        is_full_screen = (chosen_mode == "full")
        run_main_application_flow(capture_mode_is_full_screen=is_full_screen)
        
        print("MAIN_APP: Starting Gtk.main() loop to manage ScreenshotDisplayWindow.")
        Gtk.main() # This starts the main GTK loop for the ScreenshotDisplayWindow
                   # It will be quit by ScreenshotDisplayWindow's on_destroy method.
    else:
        # This case should ideally be handled by the exit after dialog.run()
        print("MAIN_APP: No mode chosen (should not happen if logic is correct). Exiting.")

    print("MAIN_APP: Application has finished.")

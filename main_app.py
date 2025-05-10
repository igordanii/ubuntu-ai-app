# main_app.py (or your main script)
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from capture_utils import capture_screen # From Phase 1
from display_window import show_screenshot # From Phase 2

def run_capture_and_display(full_screen=True):
    print(f"Starting capture (full_screen={full_screen})...")
    temp_image_path = capture_screen(full_screen=full_screen)

    if temp_image_path:
        print(f"Screenshot captured: {temp_image_path}")
        # The show_screenshot function will now be responsible for the Gtk.main() loop
        # if it's the only GTK interaction.
        # If we have a persistent main app window later, Gtk.main() will be called once.
        show_screenshot(temp_image_path, is_temporary_file=True)
        Gtk.main() # Start GTK loop to make the window visible and interactive
        print("Display window closed, Gtk.main() exited.")
    else:
        print("Screenshot capture failed or was cancelled. Nothing to display.")

if __name__ == "__main__":
    # Example: Trigger a selected area capture
    print("Choose capture type:")
    print("1. Full Screen")
    print("2. Select Area")
    choice = input("Enter choice (1 or 2): ")

    if choice == '1':
        run_capture_and_display(full_screen=True)
    elif choice == '2':
        run_capture_and_display(full_screen=False)
    else:
        print("Invalid choice.")
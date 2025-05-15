# text_assistant_main.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import os
import sys
import time
import signal 
import subprocess 

APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)
print(f"TEXT_ASSISTANT: Changed CWD to: {APP_DIR}")

try:
    from floating_action_panel import FloatingActionPanel
    from text_action_dialogs import ResultDisplayDialog
    from common_dialogs import LanguageSelectionDialog, SUPPORTED_LANGUAGES, DEFAULT_TARGET_LANGUAGE_DISPLAY
    from gemini_utils import (
        translate_text_with_gemini,
        summarize_text_with_gemini,
        improve_formatting_with_gemini,
        is_api_configured
    )
except ImportError as e:
    print(f"TEXT_ASSISTANT: Error importing modules: {e}")
    print("Ensure all .py files (floating_action_panel.py, text_action_dialogs.py, common_dialogs.py, gemini_utils.py) are present.")
    sys.exit(1)

class TextAssistantController:
    def __init__(self):
        self.floating_panel = None
        self.last_selected_language_display = DEFAULT_TARGET_LANGUAGE_DISPLAY
        self.last_successful_clipboard_text = "" # Text successfully retrieved from clipboard
        self.last_text_panel_shown_for = ""    # Text for which panel was last successfully SHOWN
        self.panel_visible = False
        self.polling_interval_ms = 750 # Polling interval

        self.floating_panel = FloatingActionPanel()
        self.floating_panel.connect("hide", self.on_floating_panel_hidden)

        print("TEXT_ASSISTANT_CONTROLLER: Initialized. Will poll clipboard using wl-paste.")

    def get_clipboard_content_wl_paste(self):
        """Fetches clipboard content using wl-paste command."""
        try:
            process = subprocess.Popen(['wl-paste', '--no-newline'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Timeout for wl-paste communicate()
            stdout, stderr = process.communicate(timeout=0.75) 

            if process.returncode == 0:
                return stdout.decode('utf-8').strip()
            else:
                # print(f"wl-paste code: {process.returncode}, stderr: {stderr.decode('utf-8').strip()}")
                return "" # Treat non-zero as empty clipboard (e.g., if clipboard has no text)
        except FileNotFoundError:
            return "WL_PASTE_NOT_FOUND" 
        except subprocess.TimeoutExpired: 
            print(f"TEXT_ASSISTANT_CONTROLLER: wl-paste timed out.")
            return None # Indicate timeout
        except Exception as e:
            print(f"TEXT_ASSISTANT_CONTROLLER: Error using wl-paste: {e}")
            return None # Indicate other error

    def poll_clipboard_content(self):
        """Periodically polls the clipboard content using wl-paste."""
        raw_text_from_wl_paste = self.get_clipboard_content_wl_paste()

        if raw_text_from_wl_paste == "WL_PASTE_NOT_FOUND":
            print("TEXT_ASSISTANT_CONTROLLER: wl-paste not found, stopping clipboard polling.")
            return False # Stop the GLib.timeout_add timer

        current_clipboard_text = ""
        # If wl-paste had an error (returned None), use the last successfully read text.
        # This prevents flickering if wl-paste temporarily fails.
        if raw_text_from_wl_paste is not None: 
            current_clipboard_text = raw_text_from_wl_paste
            self.last_successful_clipboard_text = current_clipboard_text 
        else: 
            current_clipboard_text = self.last_successful_clipboard_text
            print(f"TEXT_ASSISTANT_CONTROLLER: Using last successful clipboard text due to wl-paste issue: '{current_clipboard_text[:30]}...'")

        # Debug print for polling status
        # print(f"Poll: Current='{current_clipboard_text[:30]}', LastShown='{self.last_text_panel_shown_for[:30]}', PanelVis: {self.panel_visible}")


        if current_clipboard_text: # If there's effectively text on the clipboard (or last known good text)
            # Show panel if:
            # 1. It's not currently visible AND
            # 2. The current clipboard text is different from the text for which the panel was last shown.
            if not self.panel_visible and current_clipboard_text != self.last_text_panel_shown_for:
                print(f"TEXT_ASSISTANT_CONTROLLER: New clipboard text detected for panel: '{current_clipboard_text[:50]}...'")
                
                display = Gdk.Display.get_default()
                seat = display.get_default_seat()
                pointer = seat.get_pointer() 

                if pointer:
                    screen, x, y = pointer.get_position() 
                    
                    # Fallback for pointer position if (0,0) and screen info is available
                    if x == 0 and y == 0 and screen:
                        print(f"TEXT_ASSISTANT_CONTROLLER: Pointer at (0,0), attempting to center on screen {screen.get_number()}.")
                        monitor = display.get_monitor_at_point(0,0) 
                        if not monitor: monitor = display.get_primary_monitor() 
                        if monitor:
                            rect = monitor.get_geometry()
                            x = rect.x + rect.width // 2 - 50 # Offset slightly from center
                            y = rect.y + rect.height // 2 - 20
                        else: 
                            x = 200; y = 200 # Absolute fallback
                    
                    print(f"TEXT_ASSISTANT_CONTROLLER: Pointer position: ({x},{y}). Showing panel.")
                    
                    self.floating_panel.show_panel(x + 15, y + 15, current_clipboard_text, self.handle_float_panel_action) 
                    self.panel_visible = True
                    self.last_text_panel_shown_for = current_clipboard_text # Update text for which panel is now shown
                else:
                    print("TEXT_ASSISTANT_CONTROLLER: Could not get pointer device to position panel.")
            
        elif not current_clipboard_text: # Clipboard is now confirmed empty
             if self.panel_visible:
                 print("TEXT_ASSISTANT_CONTROLLER: Clipboard text is now empty. Hiding panel.")
                 self.floating_panel.hide() # This will trigger on_floating_panel_hidden
             self.last_text_panel_shown_for = "" 
             self.last_successful_clipboard_text = "" 
        
        return True # Keep polling

    def on_floating_panel_hidden(self, widget):
        """Callback for when the floating panel is hidden (by itself or by controller)."""
        print("TEXT_ASSISTANT_CONTROLLER: Floating panel was hidden (hide signal received).")
        self.panel_visible = False
        # Do NOT reset self.last_text_panel_shown_for here.
        # If the panel hid due to focus loss, but the clipboard content is still the same,
        # we don't want it to immediately reappear on the next poll.
        # It should only reappear if the clipboard content *changes* to something new,
        # or if the clipboard was cleared and then new text (even if it's the same as before the clear) is copied.

    def handle_float_panel_action(self, action_id, selected_text):
        """Callback from FloatingActionPanel when an action is chosen."""
        print(f"TEXT_ASSISTANT_CONTROLLER: Action '{action_id}' received for text: '{selected_text[:30]}...'")

        # Panel is likely already hidden by its own focus-out or Esc, or by user clicking an action.
        # Ensure our internal state is up-to-date.
        self.panel_visible = False 
        # After an action is initiated, clear last_text_panel_shown_for.
        # This means if the user copies the exact same text again *after* an action,
        # the panel *will* reappear, because last_text_panel_shown_for is now different.
        self.last_text_panel_shown_for = "" 
        self.last_successful_clipboard_text = "" # Also clear this to ensure fresh state for next copy


        if not selected_text: 
            self.show_result_dialog("Error", "No text was provided for the action.", "No text available.", None)
            return

        if not is_api_configured() and not os.getenv("SIMULATE_GEMINI", "True").lower() == "true":
             self.show_result_dialog("API Error", "Gemini API is not configured.",
                                     "Please ensure your GOOGLE_API_KEY is set correctly.", None)
             return

        result_title = "Result"
        action_result_text = "No result."
        dialog_parent = None # Dialogs are transient for the screen

        if action_id == "translate":
            lang_dialog = LanguageSelectionDialog(dialog_parent, self.last_selected_language_display)
            lang_response = lang_dialog.run()
            selected_lang_code = None
            selected_lang_display_name = "selected language"
            if lang_response == Gtk.ResponseType.OK:
                selected_lang_code = lang_dialog.get_selected_language_code()
                selected_lang_display_name = lang_dialog.language_combo.get_active_text()
                if selected_lang_display_name:
                    self.last_selected_language_display = selected_lang_display_name
            lang_dialog.destroy()

            if selected_lang_code:
                result_title = f"Translation to {selected_lang_display_name}"
                action_result_text = translate_text_with_gemini(selected_text, target_language=selected_lang_code)
            else:
                action_result_text = "Translation cancelled: No language selected."
        
        elif action_id == "summarize":
            result_title = "Summary"
            action_result_text = summarize_text_with_gemini(selected_text, length="medium")

        elif action_id == "format":
            result_title = "Formatted Text"
            action_result_text = improve_formatting_with_gemini(selected_text)
        
        self.show_result_dialog(result_title, f"Result for '{action_id}':", action_result_text, dialog_parent)

    def show_result_dialog(self, title, message, result_text, parent_window):
        dialog = ResultDisplayDialog(parent_window, title, message, result_text)
        dialog.run()
        dialog.destroy()

    def run(self):
        print("TEXT_ASSISTANT_CONTROLLER: Starting GTK main loop. Will poll clipboard using wl-paste.")
        GLib.timeout_add(self.polling_interval_ms, self.poll_clipboard_content)
        Gtk.main()
    
    def cleanup_on_exit(self):
        print("TEXT_ASSISTANT_CONTROLLER: Performing cleanup on exit.")
        if self.floating_panel and self.floating_panel.get_visible():
            print("TEXT_ASSISTANT: Destroying visible floating panel on exit.")
            self.floating_panel.destroy()


if __name__ == "__main__":
    print("TEXT_ASSISTANT: Starting Text Assistant application (Clipboard Polling Mode with wl-paste)...")
    
    controller = TextAssistantController()

    try:
        subprocess.run(["which", "wl-paste"], check=True, capture_output=True, timeout=1)
        print("TEXT_ASSISTANT: wl-paste found on system.")
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        print("TEXT_ASSISTANT: CRITICAL ERROR - wl-paste command not found...")
        error_dialog = Gtk.MessageDialog(transient_for=None, flags=0, message_type=Gtk.MessageType.ERROR,
                                         buttons=Gtk.ButtonsType.OK, text="Dependency Missing")
        error_dialog.format_secondary_text("wl-paste was not found. This application cannot function without it.\nPlease install 'wl-clipboard' (e.g., sudo apt install wl-clipboard) and restart.")
        error_dialog.run()
        error_dialog.destroy()
        sys.exit(1)

    def sigint_handler(*args):
        print("\nTEXT_ASSISTANT: SIGINT (Ctrl+C) received. Requesting Gtk.main_quit().")
        Gtk.main_quit()

    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, sigint_handler)
    
    if not is_api_configured() and not os.getenv("SIMULATE_GEMINI", "True").lower() == "true":
        print("TEXT_ASSISTANT: WARNING - Gemini API key not found or SIMULATE_GEMINI is False.")
    
    try:
        controller.run()
    except Exception as e:
        print(f"TEXT_ASSISTANT: An unexpected error occurred during controller.run(): {e}")
        import traceback
        traceback.print_exc()
    finally:
        controller.cleanup_on_exit()
        print("TEXT_ASSISTANT: Application has finished.")

# common_dialogs.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# --- Language Configuration (Moved here) ---
# Display Name: Language Code (for Gemini API)
SUPPORTED_LANGUAGES = {
    "Brazilian Portuguese": "pt-BR",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Chinese (Simplified)": "zh-CN",
    "Italian": "it",
    "Russian": "ru",
    "Korean": "ko"
}
DEFAULT_TARGET_LANGUAGE_DISPLAY = "Brazilian Portuguese" # The one selected by default

class LanguageSelectionDialog(Gtk.Dialog):
    def __init__(self, parent_window, default_language_display_name):
        super().__init__(title="Select Target Language", transient_for=parent_window, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.set_default_size(300, 100)
        self.set_modal(True) # Make it modal to the parent

        self.language_combo = Gtk.ComboBoxText()
        active_idx = 0
        idx_count = 0
        # Populate the ComboBoxText with display names from SUPPORTED_LANGUAGES
        for display_name in SUPPORTED_LANGUAGES.keys():
            self.language_combo.append_text(display_name)
            if display_name == default_language_display_name:
                active_idx = idx_count
            idx_count += 1
        
        self.language_combo.set_active(active_idx) # Set the default selection

        box = self.get_content_area() # This is a Gtk.Box
        box.set_spacing(10)
        box.set_border_width(10) # Add some padding around the content area
        
        label = Gtk.Label(label="Translate to:")
        label.props.xalign = 0 # Left align the label
        box.pack_start(label, False, False, 0)
        box.pack_start(self.language_combo, True, True, 0) # ComboBox expands
        
        self.show_all()

    def get_selected_language_code(self):
        """
        Returns the language code (e.g., 'pt-BR') for the currently selected
        language display name in the ComboBox.
        Returns None if no language is actively selected or found.
        """
        active_text = self.language_combo.get_active_text() # Gets the display name
        if active_text:
            return SUPPORTED_LANGUAGES.get(active_text) # Look up the code
        return None

if __name__ == '__main__':
    # Simple test for LanguageSelectionDialog
    # This allows you to run `python common_dialogs.py` to test this dialog independently.
    print("Testing LanguageSelectionDialog directly...")
    
    # Create a dummy parent window for the dialog to be transient_for
    # In a real app, this would be your main application window.
    # For a simple test, a new Gtk.Window can be used, or None if not critical for the test.
    # test_parent_window = Gtk.Window(title="Test Parent") 
    # test_parent_window.connect("destroy", Gtk.main_quit)
    # test_parent_window.show()

    dialog = LanguageSelectionDialog(None, DEFAULT_TARGET_LANGUAGE_DISPLAY)
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        selected_code = dialog.get_selected_language_code()
        selected_display = dialog.language_combo.get_active_text()
        print(f"Language selected: {selected_display} (Code: {selected_code})")
    else:
        print("Language selection cancelled or dialog closed.")
    
    dialog.destroy()
    # Gtk.main() # Only needed if you showed a persistent parent window for testing.

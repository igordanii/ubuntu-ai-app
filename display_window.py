# display_window.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib
import os
import shutil
import datetime

# Import your utility functions
from ocr_utils import extract_text_from_image
from gemini_utils import translate_text_with_gemini # Ensure this can take a target_language argument
import pyperclip

# --- Language Configuration ---
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
        for display_name in SUPPORTED_LANGUAGES.keys():
            self.language_combo.append_text(display_name)
            if display_name == default_language_display_name:
                active_idx = idx_count
            idx_count += 1
        
        self.language_combo.set_active(active_idx)

        box = self.get_content_area() # Gtk.Box
        box.set_spacing(10)
        box.set_border_width(10) # Add some padding around the content area
        
        label = Gtk.Label(label="Translate to:")
        label.props.xalign = 0 # Left align
        box.pack_start(label, False, False, 0)
        box.pack_start(self.language_combo, True, True, 0)
        
        self.show_all()

    def get_selected_language_code(self):
        active_text = self.language_combo.get_active_text()
        if active_text:
            return SUPPORTED_LANGUAGES.get(active_text)
        return None

class ScreenshotDisplayWindow(Gtk.Window):
    def __init__(self, image_path):
        super().__init__(title="Screenshot Preview")

        self.image_path = image_path
        self.temp_file_to_delete = None
        self.default_save_dir = os.path.expanduser("~/Pictures/Screenshots")
        self.last_selected_language_display = DEFAULT_TARGET_LANGUAGE_DISPLAY # Store last selection

        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        self.outer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(self.outer_box)

        # --- Image Area ---
        self.pixbuf = None
        try:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.image_path)
            screen = self.get_screen()
            if screen:
                monitor = screen.get_primary_monitor()
                monitor_geometry = screen.get_monitor_geometry(monitor)
                max_img_width = int(monitor_geometry.width * 0.85) 
                max_img_height = int(monitor_geometry.height * 0.85)
                img_width = self.pixbuf.get_width()
                img_height = self.pixbuf.get_height()
                scaled = False
                if img_width > max_img_width:
                    aspect_ratio = float(img_height) / img_width
                    img_width = max_img_width
                    img_height = int(img_width * aspect_ratio)
                    scaled = True
                if img_height > max_img_height:
                    aspect_ratio = float(img_width) / img_height
                    img_height = max_img_height
                    img_width = int(img_height * aspect_ratio)
                    scaled = True
                if scaled:
                    self.pixbuf = self.pixbuf.scale_simple(img_width, img_height, GdkPixbuf.InterpType.BILINEAR)
            image_widget = Gtk.Image.new_from_pixbuf(self.pixbuf)
            self.outer_box.pack_start(image_widget, True, True, 0)
        except GLib.Error as e:
            print(f"Error loading image '{self.image_path}': {e}")
            error_label = Gtk.Label(label=f"Error: Could not load image.\n{e}")
            self.outer_box.pack_start(error_label, True, True, 0)
            self.set_default_size(350, 150)

        # --- Buttons Area ---
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        button_box.set_margin_start(6); button_box.set_margin_end(6)
        button_box.set_margin_top(6); button_box.set_margin_bottom(6)
        self.outer_box.pack_start(button_box, False, False, 0)

        button_size = 36
        icon_size_enum = Gtk.IconSize.LARGE_TOOLBAR

        def create_icon_button(icon_name, tooltip_text, callback_method):
            button = Gtk.Button()
            try:
                icon_widget = Gtk.Image.new_from_icon_name(icon_name + "-symbolic", icon_size_enum)
                if not icon_widget.get_icon_name()[0]: 
                     icon_widget = Gtk.Image.new_from_icon_name(icon_name, icon_size_enum)
            except GLib.Error:
                 icon_widget = Gtk.Image.new_from_icon_name(icon_name, icon_size_enum)
            button.set_image(icon_widget)
            button.set_tooltip_text(tooltip_text)
            button.set_size_request(button_size, button_size)
            button.connect("clicked", callback_method)
            return button

        self.btn_save = create_icon_button("document-save", "Save Image", self.on_save_clicked)
        button_box.pack_start(self.btn_save, False, False, 0)
        self.btn_translate = create_icon_button("accessories-dictionary", "Translate Text from Image", self.on_translate_clicked)
        button_box.pack_start(self.btn_translate, False, False, 0)
        self.btn_copy_text = create_icon_button("edit-copy", "Copy Text from Image", self.on_copy_text_clicked)
        button_box.pack_start(self.btn_copy_text, False, False, 0)
        button_box.pack_start(Gtk.Box(), True, True, 0) # Spacer
        self.btn_close = create_icon_button("window-close", "Close Window (Esc)", lambda w: self.close())
        button_box.pack_start(self.btn_close, False, False, 0)

        self.connect("destroy", self.on_destroy)
        self.connect("key-press-event", self.on_key_press)

        if self.pixbuf: self.resize(1,1) 
        else: self.set_default_size(450, 250) 

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
        return False

    def set_temp_file_to_delete(self, filepath):
        self.temp_file_to_delete = filepath

    def on_destroy(self, widget):
        print("Display window destroyed.")
        if self.temp_file_to_delete and os.path.exists(self.temp_file_to_delete):
            try:
                os.remove(self.temp_file_to_delete)
                print(f"Temporary file '{self.temp_file_to_delete}' deleted.")
            except OSError as e:
                print(f"Error deleting temporary file '{self.temp_file_to_delete}': {e}")
        Gtk.main_quit()

    def on_save_clicked(self, widget):
        print("[ACTION] Save Image button clicked.")
        if not os.path.exists(self.default_save_dir):
            try:
                os.makedirs(self.default_save_dir, exist_ok=True)
            except OSError as e:
                self.show_error_dialog("Save Error", f"Could not create save directory.\n{e}")
                return
        now = datetime.datetime.now()
        filename = f"Screenshot_{now.strftime('%Y-%m-%d_%H%M%S')}.png"
        save_path = os.path.join(self.default_save_dir, filename)
        try:
            shutil.copy2(self.image_path, save_path)
            self.show_info_dialog("Image Saved", f"Screenshot saved as\n{save_path}")
        except Exception as e:
            self.show_error_dialog("Save Error", f"Could not save image to {save_path}.\n{e}")

    def on_translate_clicked(self, widget):
        print("[ACTION] Translate Text button clicked.")
        if not self.image_path or not os.path.exists(self.image_path):
            self.show_error_dialog("Translation Error", "Image path is invalid or file does not exist.")
            return

        # 1. Show language selection dialog
        lang_dialog = LanguageSelectionDialog(self, self.last_selected_language_display)
        response = lang_dialog.run()
        
        selected_lang_code = None
        selected_lang_display_name = None

        if response == Gtk.ResponseType.OK:
            selected_lang_code = lang_dialog.get_selected_language_code()
            selected_lang_display_name = lang_dialog.language_combo.get_active_text()
            if selected_lang_display_name: # Store for next time
                self.last_selected_language_display = selected_lang_display_name
            print(f"Language selected: {selected_lang_display_name} ({selected_lang_code})")
        else:
            print("Language selection cancelled.")
            lang_dialog.destroy()
            return # User cancelled

        lang_dialog.destroy() # Important to destroy the dialog

        if not selected_lang_code:
            self.show_error_dialog("Translation Error", "No target language was selected.")
            return

        # 2. Extract text using OCR
        extracted_text = extract_text_from_image(self.image_path)
        if not extracted_text:
            error_msg = "Could not extract text from the image, or no text was found."
            if isinstance(extracted_text, str) and "Error:" in extracted_text:
                error_msg = extracted_text
            self.show_error_dialog("OCR Problem", error_msg)
            return

        # 3. Translate the extracted text using Gemini
        translated_text = translate_text_with_gemini(extracted_text, target_language=selected_lang_code)

        # 4. Display the translation
        if translated_text:
            # Check for known error strings from gemini_utils or ocr_utils
            known_errors = ["Gemini API not configured", "Error during translation", "Tesseract not found", "No text provided"]
            is_error = any(err_msg in translated_text for err_msg in known_errors) and "Error:" in translated_text

            if is_error:
                self.show_error_dialog("Translation Failed", translated_text)
            else:
                self.show_info_dialog(f"Translation to {selected_lang_display_name}", translated_text)
        else:
            self.show_error_dialog("Translation Failed", "An unknown error occurred, or no translation was returned.")


    def on_copy_text_clicked(self, widget):
        print("[ACTION] Copy Text button clicked.")
        if not self.image_path or not os.path.exists(self.image_path):
            self.show_error_dialog("Copy Error", "Image path is invalid or file does not exist.")
            return
        extracted_text = extract_text_from_image(self.image_path)
        if extracted_text:
            try:
                pyperclip.copy(extracted_text)
                self.show_info_dialog("Text Copied", "Extracted text has been copied to the clipboard.")
            except pyperclip.PyperclipException as e:
                error_message = f"Could not copy text to clipboard.\nError: {e}\n" \
                                "Please ensure xclip or xsel is installed."
                self.show_error_dialog("Clipboard Error", error_message)
            except Exception as e:
                self.show_error_dialog("Clipboard Error", f"An unexpected error occurred: {e}")
        elif extracted_text == "":
            self.show_info_dialog("Copy Text", "No text was found in the image.")
        else:
            error_msg = "Could not extract text from the image."
            if isinstance(extracted_text, str) and "Error:" in extracted_text:
                error_msg = extracted_text 
            self.show_error_dialog("OCR Error", error_msg)

    # --- Helper Dialogs ---
    def show_info_dialog(self, title, message):
        dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK, text=title)
        dialog.format_secondary_text(message)
        if dialog.get_message_area():
            for child_widget in dialog.get_message_area().get_children():
                 if isinstance(child_widget, Gtk.Label):
                    child_widget.set_selectable(True); child_widget.set_line_wrap(True)
                    child_widget.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                    child_widget.props.xalign = 0
        dialog.run(); dialog.destroy()

    def show_error_dialog(self, title, message):
        dialog = Gtk.MessageDialog(transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.OK, text=title)
        dialog.format_secondary_text(message); dialog.run(); dialog.destroy()

def show_screenshot(image_path, is_temporary_file=False):
    win = ScreenshotDisplayWindow(image_path)
    if is_temporary_file:
        win.set_temp_file_to_delete(image_path)
    win.show_all()

if __name__ == "__main__":
    # This block is for testing display_window.py directly
    test_image_file = "test_image.png" 
    if not os.path.exists(test_image_file):
        print(f"Test image '{test_image_file}' not found for direct testing.")
        try:
            from PIL import Image, ImageDraw; import random
            img = Image.new('RGB', (700,450), color=(random.randint(0,100),random.randint(0,100),random.randint(0,100)))
            d = ImageDraw.Draw(img)
            d.text((20,20), "Test Image for display_window.py", fill=(255,255,0))
            d.text((20,50), f"Screen: {Gdk.Screen.get_default().get_width()}x{Gdk.Screen.get_default().get_height()}", fill=(200,200,200))
            d.text((20,80), "Test the translate button - it should show a language selection dialog.", fill=(220,220,220))
            img.save(test_image_file); print(f"Created dummy image: {test_image_file}")
        except ImportError: print("Pillow not installed. Cannot create dummy test_image.png.")
        except Exception as e: print(f"Error creating dummy image: {e}")
    if os.path.exists(test_image_file):
        print(f"Displaying test image: {test_image_file}")
        show_screenshot(test_image_file, is_temporary_file=False)
        Gtk.main()
        print("GTK main loop finished (display_window.py direct test).")
    else: print("No test_image.png found, skipping direct display test.")

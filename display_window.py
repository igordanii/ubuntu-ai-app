# display_window.py
import gi
import pyperclip
from ocr_utils import extract_text_from_image
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango, GLib # Added GLib for error checking icon loading
import os
import shutil
import datetime # For on_save_clicked filename

# We'll need these later for actual button actions.
# For now, ensure you have placeholder functions or the actual util files.
# from ocr_utils import extract_text_from_image
# from gemini_utils import translate_text_with_gemini # Or whatever you named it
# import pyperclip

# --- Placeholder for OCR and Gemini utilities (if not in separate files yet) ---
# These are just for testing the UI flow if the real utils aren't ready.
# def extract_text_from_image(image_path):
#     print(f"[OCR PREVIEW] Would extract text from: {image_path}")
#     if "text" in image_path.lower(): # Simulate finding text in some images
#         return "This is sample text from the image."
#     return "No text found (simulated)."

# def translate_text_with_gemini(text_to_translate, target_language="en"): # Ensure correct naming
#     print(f"[GEMINI PREVIEW] Would translate: '{text_to_translate}' to {target_language}")
#     return f"Translated: {text_to_translate} (to {target_language})"
# --- End Placeholders ---

class ScreenshotDisplayWindow(Gtk.Window):
    def __init__(self, image_path):
        super().__init__(title="Screenshot Preview")

        self.image_path = image_path
        self.temp_file_to_delete = None
        self.default_save_dir = os.path.expanduser("~/Pictures/Screenshots") # Default save location for screenshots

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
            # Ensure screen is available (it might not be in some testing/headless contexts)
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

        except GLib.Error as e: # More specific GLib error for file loading
            print(f"Error loading image '{self.image_path}': {e}")
            error_label = Gtk.Label(label=f"Error: Could not load image.\n{e}")
            self.outer_box.pack_start(error_label, True, True, 0)
            self.set_default_size(350, 150) # Adjusted size for error message

        # --- Buttons Area (Vertical Box on the right) ---
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        button_box.set_margin_start(6)
        button_box.set_margin_end(6)
        button_box.set_margin_top(6)
        button_box.set_margin_bottom(6)
        self.outer_box.pack_start(button_box, False, False, 0)

        button_size = 36
        icon_size_enum = Gtk.IconSize.LARGE_TOOLBAR # GTK's enum for icon size ~24px

        def create_icon_button(icon_name, tooltip_text, callback_method):
            button = Gtk.Button()
            # Try to load symbolic icon first, then fallback to regular
            # Symbolic icons are monochrome and adapt to the theme colors
            try:
                icon_widget = Gtk.Image.new_from_icon_name(icon_name + "-symbolic", icon_size_enum)
                # Check if the icon was actually loaded (some themes might not have all symbolic versions)
                # Gtk.Image.get_pixbuf() is None if icon_name is invalid or not found in theme
                # Gtk.Image.get_icon_name() returns (name, size, success) if using icon_name
                # A more robust check might involve checking the theme's capabilities or specific icon existence.
                # For simplicity, if symbolic fails, we try non-symbolic.
                if not icon_widget.get_icon_name()[0]: # If name is None, symbolic likely failed to load
                     icon_widget = Gtk.Image.new_from_icon_name(icon_name, icon_size_enum)
            except GLib.Error: # Fallback if '-symbolic' name itself is invalid before even checking load
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

        # Connect signals
        self.connect("destroy", self.on_destroy) # This was the missing method connection target
        self.connect("key-press-event", self.on_key_press)

        if self.pixbuf:
            self.resize(1,1) 
        else: # If image loading failed
            self.set_default_size(450, 250) 

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            print("Escape key pressed. Closing window.")
            self.close()
        return False # Allow other handlers to process the event if needed

    def set_temp_file_to_delete(self, filepath):
        self.temp_file_to_delete = filepath

    def on_destroy(self, widget): # <<<< THIS IS THE CORRECTED METHOD
        print("Display window destroyed.")
        if self.temp_file_to_delete and os.path.exists(self.temp_file_to_delete):
            try:
                os.remove(self.temp_file_to_delete)
                print(f"Temporary file '{self.temp_file_to_delete}' deleted.")
            except OSError as e:
                print(f"Error deleting temporary file '{self.temp_file_to_delete}': {e}")
        # If this is the only GTK window, Gtk.main() loop (called in main_app.py) will exit.

    # --- Button Action Methods ---
    def on_save_clicked(self, widget):
        print("[ACTION] Save Image button clicked.")
        if not os.path.exists(self.default_save_dir):
            try:
                os.makedirs(self.default_save_dir, exist_ok=True)
            except OSError as e:
                print(f"Error creating save directory '{self.default_save_dir}': {e}")
                self.show_error_dialog("Save Error", f"Could not create save directory.\n{e}")
                return

        now = datetime.datetime.now()
        filename = f"Screenshot_{now.strftime('%Y-%m-%d_%H%M%S')}.png"
        save_path = os.path.join(self.default_save_dir, filename)
        
        try:
            shutil.copy2(self.image_path, save_path) # copy2 preserves metadata
            print(f"Image saved to: {save_path}")
            self.show_info_dialog("Image Saved", f"Screenshot saved as\n{save_path}")
        except Exception as e:
            print(f"Error saving image: {e}")
            self.show_error_dialog("Save Error", f"Could not save image to {save_path}.\n{e}")

    def on_translate_clicked(self, widget):
        print("[ACTION] Translate Text button clicked.")
        # Placeholder for actual implementation:
        # text_to_translate = extract_text_from_image(self.image_path) # Your OCR function
        # if text_to_translate and text_to_translate.strip():
        #     translated_text = translate_text_with_gemini(text_to_translate, target_language="pt") # Your Gemini function
        #     self.show_info_dialog("Translation Result", translated_text)
        # else:
        #     self.show_info_dialog("Translation", "No text found or extracted from the image.")
        self.show_info_dialog("Translate Text", "Functionality to extract and translate text will be implemented here.")


    def on_copy_text_clicked(self, widget):
        print("[ACTION] Copy Text button clicked.")
        if not self.image_path or not os.path.exists(self.image_path):
            self.show_error_dialog("Copy Error", "Image path is invalid or file does not exist.")
            return

        extracted_text = extract_text_from_image(self.image_path)

        if extracted_text:
            try:
                pyperclip.copy(extracted_text)
                print(f"Copied to clipboard (first 100 chars): {extracted_text[:100]}...")
                self.show_info_dialog("Text Copied", "Extracted text has been copied to the clipboard.")
            except pyperclip.PyperclipException as e:
                error_message = f"Could not copy text to clipboard.\nError: {e}\n" \
                                "Please ensure xclip or xsel is installed (e.g., sudo apt install xclip)."
                print(error_message)
                self.show_error_dialog("Clipboard Error", error_message)
            except Exception as e: # Catch any other unexpected errors during copy
                print(f"Unexpected error during copy to clipboard: {e}")
                self.show_error_dialog("Clipboard Error", f"An unexpected error occurred: {e}")
        elif extracted_text == "": # OCR returned empty string (but not None)
            self.show_info_dialog("Copy Text", "No text was found in the image.")
        else: # OCR returned None or a specific error string from our wrapper
            error_msg = "Could not extract text from the image."
            if isinstance(extracted_text, str) and "Error:" in extracted_text : # If our OCR util returns specific errors
                error_msg = extracted_text 
            self.show_error_dialog("OCR Error", error_msg)


    # --- Helper Dialogs ---
    def show_info_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self, # Makes the dialog modal to this window
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        # Make text in dialog selectable and wrap
        if dialog.get_message_area(): # Message area is a Gtk.Box
            for child_widget in dialog.get_message_area().get_children():
                 if isinstance(child_widget, Gtk.Label): # Find the label with secondary text
                    child_widget.set_selectable(True)
                    child_widget.set_line_wrap(True)
                    child_widget.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR) # Wrap at word boundaries
                    child_widget.props.xalign = 0 # Left align text
        dialog.run()
        dialog.destroy()

    def show_error_dialog(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

def show_screenshot(image_path, is_temporary_file=False):
    """
    Displays a screenshot in a borderless window.
    """
    win = ScreenshotDisplayWindow(image_path)
    if is_temporary_file:
        win.set_temp_file_to_delete(image_path)
    win.show_all()
    # Gtk.main() is expected to be called by the script that calls this function,
    # e.g., main_app.py

if __name__ == "__main__":
    # This block is for testing display_window.py directly
    test_image_file = "test_image.png" 
    if not os.path.exists(test_image_file):
        print(f"Test image '{test_image_file}' not found for direct testing of display_window.py.")
        # Attempt to create a simple dummy image using Pillow (optional dependency for this test block)
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (700, 450), color = (random.randint(0,100), random.randint(0,100), random.randint(0,100))) # Dark random bg
            d = ImageDraw.Draw(img)
            d.text((20,20), "Test Image for display_window.py", fill=(255,255,0))
            d.text((20,50), f"Screen Resolution (example): {Gdk.Screen.get_default().get_width()}x{Gdk.Screen.get_default().get_height()}", fill=(200,200,200))
            d.text((20,80), "This window should be borderless, centered, and show this image with small icon buttons on the right.", fill=(220,220,220))
            d.text((20,110), "Press Esc or click the 'X' icon button to close.", fill=(220,220,220))
            img.save(test_image_file)
            print(f"Created dummy image for testing: {test_image_file}")
        except ImportError:
            print("Pillow (PIL) not installed. Cannot create dummy test_image.png automatically for testing.")
            print("Please create a 'test_image.png' manually in the same directory to test display_window.py directly.")
            # exit(1) # Or just let it proceed and potentially fail on image load if no test image
        except Exception as e:
            print(f"Error creating dummy image: {e}")
            # exit(1)
        # Import random for dummy image color, only if Pillow is being used
        import random


    if os.path.exists(test_image_file):
        print(f"Displaying test image: {test_image_file}")
        show_screenshot(test_image_file, is_temporary_file=False) # False, as it's a persistent test image
        Gtk.main() # Start the GTK main loop for direct testing
        print("GTK main loop finished (display_window.py direct test).")
    else:
        print("No test_image.png found, skipping direct display test.")
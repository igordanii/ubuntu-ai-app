# capture_mode_dialog.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib # Added Gdk for keyvals, GLib for icon loading

class CaptureModeSelectionDialog(Gtk.Dialog):
    def __init__(self, parent_window=None): # Can be transient for a main app window if one exists
        super().__init__(title="Select Capture Mode", transient_for=parent_window, flags=0)
        # No default buttons, we'll use icon buttons in the content area.
        # self.add_button("Cancel", Gtk.ResponseType.CANCEL) # Example if you want a textual cancel

        self.set_default_size(250, 150)
        self.set_modal(True)
        self.set_decorated(False) # Borderless
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        self.selected_mode = None # To store 'area' or 'full'

        content_area = self.get_content_area() # This is a Gtk.Box
        content_area.set_orientation(Gtk.Orientation.VERTICAL)
        content_area.set_spacing(15)
        content_area.set_border_width(20) # Padding inside the borderless window

        title_label = Gtk.Label(label="<b>Choose Screenshot Type</b>")
        title_label.set_use_markup(True)
        content_area.pack_start(title_label, False, False, 0)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER) # Center the button box
        content_area.pack_start(button_box, True, True, 0)

        button_size = 64  # Larger buttons for this initial dialog
        icon_size_enum = Gtk.IconSize.DIALOG # Larger icons

        # Helper to create icon buttons (similar to display_window but adapted)
        def create_mode_button(icon_name, label_text, mode_value, key_char):
            button = Gtk.Button()
            button.set_size_request(button_size + 20, button_size + 20) # Make buttons a bit taller
            
            button_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            
            try:
                icon_widget = Gtk.Image.new_from_icon_name(icon_name + "-symbolic", icon_size_enum)
                if not icon_widget.get_icon_name()[0]: 
                     icon_widget = Gtk.Image.new_from_icon_name(icon_name, icon_size_enum)
            except GLib.Error:
                 icon_widget = Gtk.Image.new_from_icon_name(icon_name, icon_size_enum)
            
            button_content_box.pack_start(icon_widget, True, True, 0)
            
            # Label with number hint
            label_widget = Gtk.Label(label=f"{label_text} ({key_char})")
            button_content_box.pack_start(label_widget, False, False, 0)
            
            button.add(button_content_box)
            button.connect("clicked", self.on_mode_selected, mode_value)
            return button

        # Icons: "view-select-region" or "image-crop" or "tool-crop"
        btn_select_area = create_mode_button("view-select-region", "Select Area", "area", "1")
        # Icons: "image-x-generic", "computer", "video-display"
        btn_full_screen = create_mode_button("video-display", "Full Screen", "full", "2")

        button_box.pack_start(btn_select_area, True, True, 0)
        button_box.pack_start(btn_full_screen, True, True, 0)

        # Connect key press event for 1 and 2
        self.connect("key-press-event", self.on_key_press)

        self.show_all()

    def on_mode_selected(self, widget, mode_value):
        print(f"Mode selected via button: {mode_value}")
        self.selected_mode = mode_value
        self.response(Gtk.ResponseType.OK) # Signal that a selection was made

    def on_key_press(self, widget, event):
        keyval = event.keyval
        if keyval == Gdk.KEY_1:
            print("Key '1' pressed for Select Area.")
            self.selected_mode = "area"
            self.response(Gtk.ResponseType.OK)
        elif keyval == Gdk.KEY_2:
            print("Key '2' pressed for Full Screen.")
            self.selected_mode = "full"
            self.response(Gtk.ResponseType.OK)
        elif keyval == Gdk.KEY_Escape:
            print("Escape pressed on mode selection. Closing.")
            self.response(Gtk.ResponseType.CANCEL)
        return False # Allow other handlers if needed

    def get_selected_mode(self):
        return self.selected_mode

if __name__ == "__main__":
    # Test the dialog directly
    dialog = CaptureModeSelectionDialog()
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        selected_mode = dialog.get_selected_mode()
        print(f"Dialog test: Selected mode: {selected_mode}")
    else:
        print("Dialog test: Cancelled or closed.")
    
    dialog.destroy()
    # Gtk.main() # Not needed if just testing dialog.run()

# floating_action_panel.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import time # For time.monotonic()

class FloatingActionPanel(Gtk.Window):
    GRACE_PERIOD_SECONDS = 0.3 # Ignore focus-out for this long after showing

    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL) 

        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_app_paintable(True) 
        self.set_skip_taskbar_hint(True) 
        self.set_skip_pager_hint(True)  

        self.set_accept_focus(False) 
        self.set_focus_on_map(False) 

        self.action_callback = None
        self.selected_text_buffer = ""
        self._show_timestamp = 0 # Timestamp of when the panel was last shown

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        main_box.set_border_width(3) 
        self.add(main_box)

        button_size = 28 
        icon_size_enum = Gtk.IconSize.SMALL_TOOLBAR 

        def create_action_button(icon_name, tooltip_text, action_id):
            button = Gtk.Button()
            try:
                icon_widget = Gtk.Image.new_from_icon_name(icon_name + "-symbolic", icon_size_enum)
                if not icon_widget.get_icon_name() or not icon_widget.get_icon_name()[0]: 
                     icon_widget = Gtk.Image.new_from_icon_name(icon_name, icon_size_enum)
            except GLib.Error: 
                 icon_widget = Gtk.Image.new_from_icon_name(icon_name, icon_size_enum)
            
            button.set_image(icon_widget)
            button.set_tooltip_text(tooltip_text)
            button.set_size_request(button_size, button_size)
            button.set_relief(Gtk.ReliefStyle.NONE) 
            button.connect("clicked", self.on_action_button_clicked, action_id)
            return button

        btn_translate = create_action_button("accessories-dictionary", "Translate Text", "translate")
        main_box.pack_start(btn_translate, False, False, 0)

        btn_summarize = create_action_button("document-properties", "Summarize Text", "summarize") 
        main_box.pack_start(btn_summarize, False, False, 0)

        btn_format = create_action_button("gtk-indent", "Improve Formatting", "format") 
        main_box.pack_start(btn_format, False, False, 0)

        self.connect("focus-out-event", self.on_focus_out)
        self.connect("key-press-event", self.on_key_press)
        self.connect("map-event", self.on_map_event)

    def on_map_event(self, widget, event):
        print("FloatingPanel: Map event. Attempting to grab focus.")
        self.grab_focus() 
        return False 

    def on_action_button_clicked(self, widget, action_id):
        print(f"FloatingPanel: Action '{action_id}' chosen.")
        self._show_timestamp = 0 # Action taken, grace period no longer needed
        if self.action_callback:
            self.action_callback(action_id, self.selected_text_buffer)
        # Controller will likely hide the panel after this.

    def on_focus_out(self, widget, event):
        # Check if we are within the grace period since the panel was shown
        if (time.monotonic() - self._show_timestamp) < self.GRACE_PERIOD_SECONDS:
            print(f"FloatingPanel: Ignoring focus-out event (within {self.GRACE_PERIOD_SECONDS}s grace period).")
            # It might be necessary to re-grab focus if we want it to stay focused.
            # GLib.idle_add(self.grab_focus)
            return True # Try to prevent hide by stopping event propagation
        
        print("FloatingPanel: Focus lost (outside grace period), hiding panel.")
        self.hide() 
        return False 

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            print("FloatingPanel: Escape pressed, hiding panel.")
            self._show_timestamp = 0 # User explicitly closed, grace period no longer needed
            self.hide() 
            return True 
        return False

    def show_panel(self, x, y, selected_text, action_callback_func, controller=None): # controller arg removed
        self.selected_text_buffer = selected_text
        self.action_callback = action_callback_func
        
        print(f"FloatingPanel: show_panel called. Moving to ({x}, {y}). Setting show_timestamp.")
        self._show_timestamp = time.monotonic() # Record when panel is shown
        
        self.set_accept_focus(True) 
        self.show_all() 
        self.move(x, y)
        
        # self.present() # Let on_map_event handle grab_focus. Presenting might also steal focus too soon.

if __name__ == '__main__':
    win = Gtk.Window(title="Test Parent for Floating Panel")
    win.set_default_size(600, 400) 
    win.connect("destroy", Gtk.main_quit)
    
    overlay = Gtk.Overlay()
    win.add(overlay)

    background_label = Gtk.Label(label="Main Window Content Area\nClick button to show panel near mouse.")
    background_label.set_halign(Gtk.Align.CENTER)
    background_label.set_valign(Gtk.Align.CENTER)
    overlay.add(background_label)
    
    floating_panel = FloatingActionPanel()

    def test_action_callback(action_id, text_content):
        print(f"--- Main Test Callback (from floating_action_panel.py test) ---")
        print(f"Action: {action_id}")
        print(f"Text: '{text_content}'")
        print(f"-------------------------------------------------------------")
        if floating_panel.get_visible():
            floating_panel.hide()

    def on_show_panel_button_clicked(widget):
        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        pointer = seat.get_pointer()

        if pointer:
            screen_obj, x, y = pointer.get_position() 
            print(f"Button click: Showing panel near mouse at screen coordinates: ({x}, {y})")
            
            floating_panel.show_panel(
                x + 10, 
                y + 10, 
                "This is some sample selected text for testing the floating panel directly.", 
                test_action_callback
            )
        else:
            print("Button click: Could not get pointer device for positioning.")
            floating_panel.show_panel(100, 100, "Fallback sample text (no pointer).", test_action_callback)

    show_button = Gtk.Button(label="Show Floating Panel (Simulate Selection)")
    show_button.connect("clicked", on_show_panel_button_clicked)
    
    show_button.set_halign(Gtk.Align.START)
    show_button.set_valign(Gtk.Align.START)
    show_button.set_margin_top(20)
    show_button.set_margin_start(20)
    overlay.add_overlay(show_button)

    win.show_all()
    Gtk.main()

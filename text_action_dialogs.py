# text_action_dialogs.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

class ActionSelectionDialog(Gtk.Dialog):
    """
    A dialog that allows the user to choose an AI action
    (Translate, Summarize, Improve Format) for the selected text.
    """
    def __init__(self, parent_window):
        super().__init__(title="Select AI Action", transient_for=parent_window, flags=0)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        # We don't add an OK button as actions are triggered by specific buttons below

        self.set_default_size(300, 200)
        self.set_modal(True)
        self.selected_action = None # To store "translate", "summarize", "format"

        content_area = self.get_content_area()
        content_area.set_spacing(15)
        content_area.set_border_width(10)

        title_label = Gtk.Label(label="<b>Choose an action for the selected text:</b>")
        title_label.set_use_markup(True)
        content_area.pack_start(title_label, False, False, 5)

        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_area.pack_start(button_box, True, True, 0)

        btn_translate = Gtk.Button(label="🌐 Translate Text")
        btn_translate.connect("clicked", self.on_action_selected, "translate")
        button_box.pack_start(btn_translate, True, True, 0)

        btn_summarize = Gtk.Button(label="✍️ Summarize Text")
        btn_summarize.connect("clicked", self.on_action_selected, "summarize")
        button_box.pack_start(btn_summarize, True, True, 0)

        btn_format = Gtk.Button(label="💅 Improve Formatting")
        btn_format.connect("clicked", self.on_action_selected, "format")
        button_box.pack_start(btn_format, True, True, 0)
        
        self.show_all()

    def on_action_selected(self, widget, action_name):
        self.selected_action = action_name
        self.response(Gtk.ResponseType.OK) # Signal that an action was chosen

    def get_selected_action(self):
        return self.selected_action

class ResultDisplayDialog(Gtk.Dialog):
    """
    A simple dialog to display text results (e.g., translation, summary).
    """
    def __init__(self, parent_window, title, message_text, result_text):
        super().__init__(title=title, transient_for=parent_window, flags=0)
        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        self.set_default_size(500, 350) # Make it a bit larger for results
        self.set_modal(True)
        self.set_border_width(10)

        content_area = self.get_content_area()
        content_area.set_spacing(10)

        if message_text: # Optional introductory message
            message_label = Gtk.Label(label=message_text)
            message_label.set_line_wrap(True)
            message_label.props.xalign = 0 # Left align
            content_area.pack_start(message_label, False, False, 5)

        # Scrolled window for the result text
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN) # Border around text view
        content_area.pack_start(scrolled_window, True, True, 0)

        text_view = Gtk.TextView()
        text_view.set_editable(False) # Read-only
        text_view.set_cursor_visible(False)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR) # Wrap text
        
        text_buffer = text_view.get_buffer()
        text_buffer.set_text(result_text if result_text else "No result to display.")
        
        scrolled_window.add(text_view)
        
        self.show_all()

if __name__ == "__main__":
    # Test ActionSelectionDialog
    print("Testing ActionSelectionDialog...")
    action_dialog = ActionSelectionDialog(None)
    response = action_dialog.run()

    if response == Gtk.ResponseType.OK:
        action = action_dialog.get_selected_action()
        print(f"Selected action: {action}")

        # Test ResultDisplayDialog based on action
        if action:
            result_dialog = ResultDisplayDialog(None, 
                                                f"Test Result for {action.capitalize()}", 
                                                f"This is a test display for the '{action}' action.",
                                                f"This would be the actual {action} result text.\n" * 5)
            result_dialog.run()
            result_dialog.destroy()

    else:
        print("Action selection cancelled.")
    action_dialog.destroy()

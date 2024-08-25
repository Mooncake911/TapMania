from typing import Callable
import customtkinter as ctk


class MyToplevelWindow(ctk.CTkToplevel):
    def __init__(self, app, message):
        super().__init__(app)
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.title("App Error")
        self.label = ctk.CTkLabel(self, text=message, justify="center")
        self.label.pack(padx=100, pady=100)


class MyInputFrame(ctk.CTkFrame):
    def __init__(self, parent, text: str, placeholder_text: str, validate_cmd):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.label = ctk.CTkLabel(self, text=text)
        self.label.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky="w")

        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder_text,
                                  validate="key", validatecommand=validate_cmd)
        self.entry.grid(row=1, column=0, padx=(10, 10), pady=(0, 10), sticky="ew")

    def get(self, default_value=""):
        if not self.entry.get():
            self.entry.insert(0, default_value)
        return self.entry.get().strip()


class MyOptionFrame(ctk.CTkFrame):
    def __init__(self, parent, text: str, values: list | tuple, command: Callable = None):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.label = ctk.CTkLabel(self, text=text)
        self.label.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky="w")

        self.option_menu = ctk.CTkOptionMenu(self, values=values, command=command)
        self.option_menu.grid(row=1, column=0, padx=(10, 10), pady=(0, 10), sticky="ew")

    def get(self):
        return self.option_menu.get().strip()


class MyInputManagerFrame(ctk.CTkFrame):
    def __init__(self, parent, button_text: str, name_placeholder_text: str, value_placeholder_text: str):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.name_placeholder_text = name_placeholder_text
        self.value_placeholder_text = value_placeholder_text

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky="nsew")

        self.add_button = ctk.CTkButton(self, text=button_text, command=self.add_input_field)
        self.add_button.grid(row=1, column=0, padx=(10, 10), pady=(10, 10), sticky="ew")

        self.input_fields = []

    def add_input_field(self):
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.pack(pady=(5, 5), padx=(10, 10), fill="x")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=3)
        frame.grid_columnconfigure(2, weight=0)

        name_field = ctk.CTkEntry(frame, placeholder_text=self.name_placeholder_text)
        name_field.grid(row=0, column=0, padx=(0, 5), pady=(0, 0), sticky="w")

        value_field = ctk.CTkEntry(frame, placeholder_text=self.value_placeholder_text)
        value_field.grid(row=0, column=1, padx=(0, 5), pady=(0, 0), sticky="we")

        delete_button = ctk.CTkButton(frame, text="Delete", command=lambda: self.remove_field_event(frame))
        delete_button.grid(row=0, column=2, padx=(0, 0), pady=(0, 0), sticky="e")

        self.input_fields.append((name_field, value_field, frame))

    def remove_field_event(self, frame):
        for name_field, value_field, f in self.input_fields:
            if f == frame:
                self.input_fields.remove((name_field, value_field, frame))
                frame.destroy()
                break

    def get(self, default_name=None, default_value=None):
        to_remove = []
        for name_field, value_field, frame in self.input_fields:
            if not name_field.get() and default_name:
                name_field.insert(0, default_name())
            if not value_field.get() and default_value:
                value_field.insert(0, default_value())
            if not name_field.get() or not value_field.get():
                to_remove.append((name_field, value_field, frame))

        for name_field, value_field, frame in to_remove:
            self.input_fields.remove((name_field, value_field, frame))
            frame.destroy()

        values = []
        for name_field, value_field, _ in self.input_fields:
            values.append((name_field.get().strip(), value_field.get().strip()))

        return values


class MyCheckboxFrame(ctk.CTkFrame):
    def __init__(self, parent, size: tuple, checkbox_texts: list[str]):
        super().__init__(parent)
        self.grid_rows, self.grid_columns = size
        [self.grid_rowconfigure(i, weight=1) for i in range(self.grid_rows)]
        [self.grid_columnconfigure(j, weight=1) for j in range(self.grid_columns)]

        self.checkboxes = {}

        for index, text in enumerate(checkbox_texts):
            row = index // self.grid_columns
            column = index % self.grid_columns
            checkbox = ctk.CTkCheckBox(self, text=text)
            checkbox.grid(row=row, column=column, padx=(10, 10), pady=(5, 5), sticky="w")
            self.checkboxes[text] = checkbox

    def get(self):
        return {text: checkbox.get() for text, checkbox in self.checkboxes.items()}

import customtkinter as ctk
from typing import Callable

# Appearance settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("themes/carrot.json")


class MyInputFrame(ctk.CTkFrame):
    def __init__(self, parent, text: str, placeholder_text: str):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.label = ctk.CTkLabel(self, text=text)
        self.label.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky="w")

        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder_text)
        self.entry.grid(row=1, column=0, padx=(10, 10), pady=(0, 10), sticky="ew")

    def get(self):
        return self.entry.get()


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
        return self.option_menu.get()


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

        self.input_fields.append(frame)

    def remove_field_event(self, frame):
        if frame in self.input_fields:
            self.input_fields.remove(frame)
            frame.destroy()


class MyCheckboxFrame(ctk.CTkFrame):
    def __init__(self, parent, size: tuple, checkbox_texts: list[str]):
        super().__init__(parent)
        self.grid_rows, self.grid_columns = size
        [self.grid_rowconfigure(i, weight=1) for i in range(self.grid_rows)]
        [self.grid_columnconfigure(j, weight=1) for j in range(self.grid_columns)]

        self.checkboxes = []

        for index, text in enumerate(checkbox_texts):
            row = index // self.grid_columns
            column = index % self.grid_columns
            checkbox = ctk.CTkCheckBox(self, text=text)
            checkbox.grid(row=row, column=column, padx=(10, 10), pady=(5, 5), sticky="w")
            self.checkboxes.append(checkbox)

    def get_checked(self):
        return [checkbox.get() for checkbox in self.checkboxes]


class MainPage(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.parent.resizable(True, True)

        self.configure(fg_color="orange", corner_radius=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Левая панель
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(4, weight=1)

        self.title_label = ctk.CTkLabel(self.left_frame, text="Hamster Kombat Farm", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.platform_frame = MyOptionFrame(self.left_frame, text="Choose Platform:",
                                            values=("android", "android_x", "ios"))
        self.platform_frame.grid(row=1, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.clicks_count_frame = MyInputFrame(self.left_frame, text="Clicks Count:", placeholder_text="Enter number")
        self.clicks_count_frame.grid(row=2, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.threads_count_frame = MyInputFrame(self.left_frame, text="Threads Count:",
                                                placeholder_text="Enter number")
        self.threads_count_frame.grid(row=3, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.appearance_mode_frame = MyOptionFrame(self.left_frame, text="Appearance Mode:",
                                                   values=("Light", "Dark", "System"),
                                                   command=self.appearance_mode_event)
        self.appearance_mode_frame.grid(row=4, column=0, padx=(10, 10), pady=(10, 5), sticky="sew")

        # Правая панель
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure((0, 2), weight=1)

        self.src_frame = MyInputManagerFrame(self.right_frame, button_text="+ Add Telegram Account",
                                             name_placeholder_text="name", value_placeholder_text="src")
        self.src_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.checkbox_frame = MyCheckboxFrame(self.right_frame, size=(2, 3),
                                              checkbox_texts=["Show", "Show", "Show", "Show", "Show", "Show"])
        self.checkbox_frame.grid(row=1, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.launch_button = ctk.CTkButton(self.right_frame, text="Start Farming", command=self.start_farm_event)
        self.launch_button.grid(row=2, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

    @staticmethod
    def appearance_mode_event(mode: str):
        ctk.set_appearance_mode(mode)

    def start_farm_event(self):
        pass

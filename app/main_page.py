import os
import uuid
import customtkinter as ctk

from .core import HamsterFarm
from .my_widgets import MyToplevelWindow, MyInputFrame, MyInputManagerFrame, MyOptionFrame, MyCheckboxFrame

base_path = os.path.dirname(__file__)


# Appearance settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme(os.path.join(base_path, "themes", "carrot.json"))


def validate_numeric_input(value: str) -> bool:
    if value == "":
        return True
    return value.isnumeric()


class MainPage(ctk.CTkFrame):
    error_window = None

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.parent.resizable(True, True)

        self.configure(fg_color="orange", corner_radius=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.hamster_farm = HamsterFarm()
        self.is_farming = False

        # Команды валидации
        validate_numeric_cmd = self.register(validate_numeric_input)

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

        self.timeout_frame = MyInputFrame(self.left_frame, text="Timout:", placeholder_text="10",
                                          validate_cmd=(validate_numeric_cmd, "%P"))
        self.timeout_frame.grid(row=2, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.num_clicks_frame = MyInputFrame(self.left_frame, text="Num Clicks:", placeholder_text="100",
                                             validate_cmd=(validate_numeric_cmd, "%P"))
        self.num_clicks_frame.grid(row=3, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.appearance_frame = MyOptionFrame(self.left_frame, text="Appearance Mode:",
                                              values=("Light", "Dark", "System"),
                                              command=self.appearance_mode_event)
        self.appearance_frame.grid(row=4, column=0, padx=(10, 10), pady=(10, 5), sticky="sew")

        # Правая панель
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure((0, 2), weight=1)

        self.users_frame = MyInputManagerFrame(self.right_frame, button_text="+ Add Telegram Account",
                                               name_placeholder_text="name", value_placeholder_text="src")
        self.users_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.checkbox_frame = MyCheckboxFrame(self.right_frame, size=(2, 3),
                                              checkbox_texts=["Headless Mode", "Claim Daily Rewards"])
        self.checkbox_frame.grid(row=1, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.launch_button = ctk.CTkButton(self.right_frame, text="Start Farming", font=("Aral", 24), fg_color="green",
                                           command=self.toggle_farming_event)
        self.launch_button.grid(row=2, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

    @staticmethod
    def appearance_mode_event(mode: str):
        ctk.set_appearance_mode(mode)

    def update_farm_parameters(self):
        self.hamster_farm.platform = str(self.platform_frame.get())
        self.hamster_farm.timeout = int(self.timeout_frame.get(default_value="10"))
        self.hamster_farm.num_clicks = int(self.num_clicks_frame.get(default_value="100"))
        self.hamster_farm.users = list(self.users_frame.get(default_name=lambda: uuid.uuid4()))
        self.hamster_farm.headless = bool(self.checkbox_frame.get()["Headless Mode"])
        self.hamster_farm.claim_daily_rewards = bool(self.checkbox_frame.get()["Claim Daily Rewards"])

        if not self.hamster_farm.platform:
            self.error_event(f"Platform is empty!")
            return False

        if not self.hamster_farm.timeout:
            self.error_event(f"Timeout is empty!")
            return False

        if not self.hamster_farm.num_clicks:
            self.error_event(f"Num Clicks is empty!")
            return False

        if not self.hamster_farm.users:
            self.error_event(f"Telegram Account List is empty!")
            return False

        return True

    def toggle_farming_event(self):
        if self.is_farming:
            self.is_farming = self.hamster_farm.deactivate_farm()
            self.launch_button.configure(text="Start Farming", fg_color="green")

        elif self.update_farm_parameters():
            self.is_farming = self.hamster_farm.activate_farm()
            self.launch_button.configure(text="Stop Farming", fg_color="red")

        else:
            pass

    def error_event(self, massage):
        if self.error_window is None or not self.error_window.winfo_exists():
            self.error_window = MyToplevelWindow(self, massage)
        else:
            self.error_window.focus()

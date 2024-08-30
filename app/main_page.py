import os
import uuid
import json
import threading
import customtkinter as ctk

from .core import HamsterFarm
from .my_widgets import (MyToplevelWindow,
                         MyInputFrame,
                         MyInputManagerFrame,
                         MyOptionFrame,
                         MyCheckboxFrame,
                         MyFileFrame)

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
        self.left_frame.grid(row=0, column=0, padx=(10, 5), pady=(10, 10), sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(5, weight=1)

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

        self.file_frame = MyFileFrame(self.left_frame, text="Configuration File:",
                                      load_text="Load Configuration", save_text="Save Configuration",
                                      load_fun=self.load_config_event, save_fun=self.save_config_event)
        self.file_frame.grid(row=4, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.appearance_frame = MyOptionFrame(self.left_frame, text="Appearance Mode:",
                                              values=("Light", "Dark", "System"),
                                              command=self.appearance_mode_event)
        self.appearance_frame.grid(row=5, column=0, padx=(10, 10), pady=(10, 10), sticky="sew")

        # Правая панель
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=(5, 10), pady=(10, 10), sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure((0, 2), weight=1)

        self.users_frame = MyInputManagerFrame(self.right_frame, button_text="+ Add Telegram Account",
                                               name_placeholder_text="name", value_placeholder_text="src")
        self.users_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.checkbox_frame = MyCheckboxFrame(self.right_frame, size=(2, 3),
                                              checkbox_texts=["Headless Mode",
                                                              "Claim Daily Rewards",
                                                              "Use Energy Boosts"])
        self.checkbox_frame.grid(row=1, column=0, padx=(10, 10), pady=(10, 5), sticky="nsew")

        self.launch_button = ctk.CTkButton(self.right_frame, text="Start Farming", font=("Aral", 24), fg_color="green",
                                           command=self.toggle_farming_event)
        self.launch_button.grid(row=2, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

    def update_farm_parameters(self):
        self.hamster_farm.platform = str(self.platform_frame.get())
        self.hamster_farm.timeout = int(self.timeout_frame.get(default_value="10"))
        self.hamster_farm.num_clicks = int(self.num_clicks_frame.get(default_value="100"))
        self.hamster_farm.users = list(self.users_frame.get(default_name=lambda: uuid.uuid4()))
        self.hamster_farm.headless = bool(self.checkbox_frame.get()["Headless Mode"])
        self.hamster_farm.claim_daily_rewards = bool(self.checkbox_frame.get()["Claim Daily Rewards"])
        self.hamster_farm.use_energy_boosts = bool(self.checkbox_frame.get()["Use Energy Boosts"])

        if not self.hamster_farm.platform:
            return f"Platform is empty!"

        if not self.hamster_farm.timeout:
            return f"Timeout is empty!"

        if not self.hamster_farm.num_clicks:
            return f"Num Clicks is empty!"

        if not self.hamster_farm.users:
            return f"Telegram Account List is empty!"

    def toggle_farming_event(self):

        def stop_farming():
            self.hamster_farm.deactivate_farm()
            self.after(0, lambda: self.launch_button.configure(text="Start Farming", fg_color="green", state="normal"))

        def start_farming():
            self.hamster_farm.activate_farm()
            self.after(0, lambda: self.launch_button.configure(text="Stop Farming", fg_color="red", state="normal"))

        if self.is_farming:
            self.is_farming = False
            self.launch_button.configure(text="Don't interrupt", fg_color="gray", state="disabled")
            threading.Thread(name="Stop Farming", target=stop_farming, daemon=True).start()

        else:
            update_massage = self.update_farm_parameters()
            if update_massage is None:
                self.is_farming = True
                self.launch_button.configure(text="Don't interrupt", fg_color="gray", state="disabled")
                threading.Thread(name="Start Farming", target=start_farming, daemon=True).start()
            else:
                self.error_event(f"Telegram Account List is empty!")

    @staticmethod
    def appearance_mode_event(mode: str):
        ctk.set_appearance_mode(mode)

    def load_config_event(self, file_path: str):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                config_data = json.load(f)
                self.platform_frame.set(config_data["platform"])
                self.timeout_frame.set(config_data["timeout"])
                self.num_clicks_frame.set(config_data["num_clicks"])
                self.users_frame.set(config_data["users"])
                self.checkbox_frame.set(config_data["checkboxes"])
        else:
            self.error_event(f"Can't load to file:\n{file_path}\n- because it's not found!")

    def save_config_event(self, file_path: str):
        dir_path = os.path.dirname(file_path)
        if os.path.exists(dir_path):
            if os.access(dir_path, os.W_OK):
                config_data = {
                    "platform": self.platform_frame.get(),
                    "timeout": self.timeout_frame.get(default_value="10"),
                    "num_clicks": self.num_clicks_frame.get(default_value="100"),
                    "users": self.users_frame.get(default_name=lambda: uuid.uuid4()),
                    "checkboxes": self.checkbox_frame.get(),
                }
                with open(file_path, "w") as config:
                    config.write(json.dumps(config_data, indent=4))
            else:
                self.error_event(f"Can't save to directory:\n{dir_path}\n- because has no write permission!")
        else:
            self.error_event(f"Can't save to directory:\n{dir_path}\n- because it's not found!")

    def error_event(self, massage):
        if self.error_window is None or not self.error_window.winfo_exists():
            self.error_window = MyToplevelWindow(self, massage)
        else:
            self.error_window.focus()

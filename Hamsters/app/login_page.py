import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps

from Hamsters.bd import redis_manager

# Appearance settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("themes/carrot.json")


def round_corners(image, radius):
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius, fill=255)

    rounded_image = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)

    return rounded_image


class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, app, message):
        super().__init__(app)
        self.resizable(False, False)
        self.title("Enter Error")

        self.label = ctk.CTkLabel(self, text=message, justify="center")
        self.label.pack(padx=20, pady=20)

        self.attributes("-topmost", True)


class LoginPage(ctk.CTkFrame):
    username = ""
    password = ""

    storage = {}
    password_attempts = 0

    toplevel_window = None

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.parent.resizable(False, False)

        self.configure(fg_color="orange", corner_radius=0)

        # Левая панель
        self.image_frame = ctk.CTkFrame(self)
        self.image_frame.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        original_image = Image.open("images/hamsters.png")
        rounded_image = round_corners(original_image, radius=25)
        self.bg_image = ctk.CTkImage(dark_image=rounded_image, light_image=rounded_image, size=(500, 500))
        self.bg_label = ctk.CTkLabel(self.image_frame, image=self.bg_image, text="", bg_color="orange")
        self.bg_label.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        # Правая панель
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.grid(row=0, column=1, padx=(50, 40), pady=(0, 40), sticky="ew")

        self.title_label = ctk.CTkLabel(self.login_frame, font=("Arial", 24, "bold"),
                                        text="Welcome Back!\nEnter to Account 🐹")
        self.title_label.grid(row=0, column=0, padx=(30, 30), pady=(40, 10), sticky="ew")

        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Telegram ID", height=35)
        self.username_entry.grid(row=1, column=0, padx=(30, 30), pady=(10, 10), sticky="nsew")

        self.image_eye = ctk.CTkImage(dark_image=Image.open("images/hear_no_evil.png"),
                                      light_image=Image.open("images/hear_no_evil.png"),
                                      size=(20, 20))
        self.image_eye_splash = ctk.CTkImage(dark_image=Image.open("images/see_no_evil.png"),
                                             light_image=Image.open("images/see_no_evil.png"),
                                             size=(20, 20))

        self.password_frame = ctk.CTkFrame(self.login_frame,
                                           bg_color=self.login_frame._bg_color,
                                           fg_color=self.login_frame._fg_color)
        self.password_frame.grid_columnconfigure(0, weight=1)
        self.password_frame.grid_columnconfigure(1, weight=0)
        self.password_entry = ctk.CTkEntry(self.password_frame, placeholder_text="Your password", height=35, show="*")
        self.password_entry.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.toggle_button = ctk.CTkButton(self.password_frame, text="", image=self.image_eye_splash, width=10,
                                           command=self.toggle_event, cursor="hand2")
        self.toggle_button.grid(row=0, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.password_frame.grid(row=2, column=0, padx=(30, 30), pady=(10, 10), sticky="nsew")

        self.login_button = ctk.CTkButton(self.login_frame, text="Enter", height=40,
                                          command=self.login_event, cursor="hand2")
        self.login_button.grid(row=3, column=0, padx=(30, 30), pady=(10, 35), sticky="nsew")
        self.password_entry.bind('<Return>', lambda event: self.login_event())

    def toggle_event(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.toggle_button.configure(image=self.image_eye)
        else:
            self.password_entry.configure(show="*")
            self.toggle_button.configure(image=self.image_eye_splash)

    def login_event(self):
        username = self.username_entry.get().replace(" ", "")
        password = self.password_entry.get().replace(" ", "")
        # redis_manager.set_user_data(telegram_id=username, password=password) возможность добавить пользователя

        if len(self.storage) < 3 and self.password_attempts < 3:

            if not self.storage.get(username, None):
                self.storage[username] = redis_manager.get_user_data(telegram_id=username)

            user_data = self.storage[username]

            if user_data:

                if int(user_data.get('online_status')) == 1:
                    self.enter_error_event(f"Access was denied due to an open session.\n"
                                           f"If it wasn't you, change your password!\n"
                                           f"@hamsters_farm_bot")

                elif int(user_data.get('online_status')) == 0 and user_data.get('password') == password:
                    self.parent.show_main_page()
                    self.username = username
                    self.password = password
                    redis_manager.update_user_status(telegram_id=username, online_status=1)

                else:
                    self.password_attempts += 1
                    self.enter_error_event(f"Password: {password} - is not correct!")

            else:
                self.enter_error_event(f"Telegram ID: {username} - is not correct!")

        else:
            self.enter_error_event(f"You was blocked!")

    def enter_error_event(self, massage):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self, massage)
        else:
            self.toplevel_window.focus()

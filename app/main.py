import os
import customtkinter as ctk

from bd import redis_manager

from .login_page import LoginPage
from .main_page import MainPage


base_path = os.path.dirname(__file__)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.attributes('-topmost', True)
        self.title("Hamster Kombat Farm")
        self.iconbitmap(os.path.join(base_path, "images", "hamster.ico"))
        self.geometry("899x499")

        self.login_page = LoginPage(self, corner_radius=0)
        self.main_page = MainPage(self, corner_radius=0)

        self.show_login_page()
        self.attributes('-topmost', False)

    def show_login_page(self):
        self.main_page.pack_forget()
        self.login_page = LoginPage(self)
        self.login_page.pack(fill="both", expand=True)

    def show_main_page(self):
        self.login_page.pack_forget()
        self.main_page = MainPage(self)
        self.main_page.pack(fill="both", expand=True)

    def close(self):
        if self.login_page.username:
            redis_manager.update_user_status(telegram_id=self.login_page.username, online_status=0)

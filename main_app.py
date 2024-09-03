from app import App

if __name__ == "__main__":
    hamster_app = App()
    try:
        hamster_app.mainloop()
    finally:
        hamster_app.close()

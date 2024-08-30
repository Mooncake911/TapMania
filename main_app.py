import signal
import sys
from app import App


def signal_handler(sig, frame):
    hamster_app.close()
    sys.exit(0)


if __name__ == "__main__":
    hamster_app = App()

    signal.signal(signal.SIGINT, signal_handler)  # Обработка Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Обработка SIGTERM

    try:
        hamster_app.mainloop()
    finally:
        hamster_app.close()

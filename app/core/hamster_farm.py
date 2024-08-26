import threading
from typing import List, Tuple
from dataclasses import dataclass, field


from .hamster_helper import HamsterHelper
from .logging_config import logger


@dataclass
class HamsterFarm:
    timeout: int = 10
    num_clicks: int = 500
    platform: str = "android"
    headless: bool = False
    claim_daily_rewards: bool = False

    users: List[Tuple[str, str]] = field(default_factory=list)
    threads: List[threading.Thread] = field(default_factory=list)
    tap_list: List[HamsterHelper] = field(default_factory=list)

    def user_start_farming(self, name, src):
        tap_halper = HamsterHelper(name=name, src=src, platform=self.platform,
                                   timeout=self.timeout,
                                   num_clicks=self.num_clicks,
                                   headless=self.headless,
                                   claim_daily_rewards=self.claim_daily_rewards)
        self.tap_list.append(tap_halper)
        tap_halper.start()

    def activate_farm(self):
        try:
            self.threads = []
            for n, user in enumerate(self.users):
                thread = threading.Thread(name=f"Thread {n}", target=self.user_start_farming, args=user, daemon=True)
                self.threads.append(thread)

            for thread in self.threads:
                thread.start()

            logger.info(f"Программа Hamster Kombat Farm запущена.")
            return True

        except Exception as e:
            self.deactivate_farm()
            logger.info(f"Поймана ошибка: {e}")

    def deactivate_farm(self):
        try:
            for tap in self.tap_list:
                tap.stop_event.set()

            logger.info(f"Программа Hamster Kombat Farm завершена.")
            return False

        except Exception as e:
            logger.info(f"Поймана ошибка: {e}")


if __name__ == '__main__':
    nasty = ("Nasty", "https://hamsterkombat.io/clicker#tgWebAppData=query_id%3DAAHDoJNgAAAAAMOgk2D94HHZ%26user%3D%257B%2522id%2522%253A1620287683%252C%2522first_name%2522%253A%2522Melissa%2522%252C%2522last_name%2522%253A%2522Pushina%2522%252C%2522username%2522%253A%2522Melissa_pushina%2522%252C%2522language_code%2522%253A%2522ru%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1724428431%26hash%3D164395524ec2cb7fa42b6b96ceecda4c561e3378393b2876c83af2028af40bb7&tgWebAppVersion=7.6&tgWebAppPlatform=web&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%233390ec%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23707579%22%2C%22link_color%22%3A%22%2300488f%22%2C%22secondary_bg_color%22%3A%22%23f4f4f5%22%2C%22text_color%22%3A%22%23000000%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22accent_text_color%22%3A%22%233390ec%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%233390ec%22%2C%22subtitle_text_color%22%3A%22%23707579%22%2C%22destructive_text_color%22%3A%22%23df3f40%22%7D")
    vadim = ("Vadim", "https://hamsterkombat.io/clicker#tgWebAppData=query_id%3DAAG_TO5fAAAAAL9M7l95GfNN%26user%3D%257B%2522id%2522%253A1609452735%252C%2522first_name%2522%253A%2522Vadim%2522%252C%2522last_name%2522%253A%2522Noodle%2522%252C%2522username%2522%253A%2522Vadim_noodle%2522%252C%2522language_code%2522%253A%2522ru%2522%252C%2522is_premium%2522%253Atrue%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1723906952%26hash%3D26844b1efa02bb307b68c1724f380e3a11caac9e3d436ab09f87712f53d3723a&amp;tgWebAppVersion=7.6&amp;tgWebAppPlatform=web&amp;tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22button_color%22%3A%22%233390ec%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23707579%22%2C%22link_color%22%3A%22%2300488f%22%2C%22secondary_bg_color%22%3A%22%23f4f4f5%22%2C%22text_color%22%3A%22%23000000%22%2C%22header_bg_color%22%3A%22%23ffffff%22%2C%22accent_text_color%22%3A%22%233390ec%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22section_header_text_color%22%3A%22%233390ec%22%2C%22subtitle_text_color%22%3A%22%23707579%22%2C%22destructive_text_color%22%3A%22%23df3f40%22%7D")
    hamster_farm = HamsterFarm()
    hamster_farm.users = [nasty, vadim]
    hamster_farm.activate_farm()

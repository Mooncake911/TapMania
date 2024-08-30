from logging_config import logger

import threading
from typing import List, Tuple
from dataclasses import dataclass, field


from .hamster_helper import HamsterHelper


@dataclass
class HamsterFarm:
    timeout: int = 10
    num_clicks: int = 500
    platform: str = "android"
    headless: bool = False
    claim_daily_rewards: bool = False
    use_energy_boosts: bool = False

    users: List[Tuple[str, str]] = field(default_factory=list)
    threads: List[threading.Thread] = field(default_factory=list)
    tap_list: List[HamsterHelper] = field(default_factory=list)

    def user_start_farming(self, name, src):
        tap_halper = HamsterHelper(name=name, src=src, platform=self.platform,
                                   timeout=self.timeout,
                                   num_clicks=self.num_clicks,
                                   headless=self.headless,
                                   claim_daily_rewards=self.claim_daily_rewards,
                                   use_energy_boosts=self.use_energy_boosts)
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

        except Exception as e:
            self.deactivate_farm()
            logger.info(f"Поймана ошибка: {e}")

    def deactivate_farm(self):
        try:
            for tap_halper in self.tap_list:
                tap_halper.stop()

            for thread in self.threads:
                thread.join(timeout=30)

            logger.info(f"Программа Hamster Kombat Farm завершена.")

        except Exception as e:
            logger.info(f"Поймана ошибка: {e}")


if __name__ == '__main__':
    user1 = ("user1", "src")
    user2 = ("user2", "src")
    hamster_farm = HamsterFarm()
    hamster_farm.users = [user1, user2]
    hamster_farm.activate_farm()

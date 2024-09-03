from logging_config import logger

from threading import Lock
from typing import Union, Optional
from redis import Redis

from config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT


class RedisManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize(*args, **kwargs)
            return cls._instance

    def _initialize(self, db: int = 0):
        """
        Инициализирует подключение к базе данных Redis.
        Этот метод вызывается только один раз при первом создании экземпляра.

        Аргументы:
        - port: порт Redis (по умолчанию 13930)
        - db: номер базы данных Redis (по умолчанию 0)
        """
        try:
            self.db = Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=db, decode_responses=True)
            logger.info("Successfully connected to Redis.")
        except Exception as e:
            self.db = None
            logger.error(f"Error connecting to Redis: {e}")

    def keys(self):
        return self.db.keys('*')

    def set_user_data(self, telegram_id: str, password: str, online_status: Union[int, bool] = 0) -> bool:
        """
        Метод для добавления или обновления данных пользователя в Redis.

        Аргументы:
        - telegram_id: ID пользователя в Telegram, который будет использоваться в качестве ключа.
        - password: пароль пользователя.
        - online_status: статус пользователя (0 | False = offline, 1 | True = online).

        Возвращает True, если данные успешно добавлены или обновлены в Redis, и False в противном случае.
        """
        if self.db:
            try:
                key = f"user:{telegram_id}"
                user_data = {
                    'password': str(password),
                    'online_status': str(int(online_status))
                }
                self.db.hset(key, mapping=user_data)
                logger.info(f"User data with Telegram ID {telegram_id} has been successfully added/updated in Redis.")
                return True
            except Exception as e:
                logger.error(f"Error adding user data to Redis: {e}")
                return False
        else:
            logger.error("No connection to Redis.")
            return False

    def get_user_data(self, telegram_id: str) -> Optional[dict]:
        """
        Метод для получения данных пользователя из Redis по Telegram ID.

        Аргументы:
        - telegram_id: ID пользователя в Telegram, по которому данные будут извлечены.

        Возвращает словарь с данными пользователя, если они существуют, и None в противном случае.
        """
        if self.db:
            try:
                key = f"user:{telegram_id}"
                data = self.db.hgetall(key)
                if data:
                    logger.info(f"User data with Telegram ID {telegram_id} was successfully retrieved from Redis.")
                    return data
                else:
                    logger.info(f"Data for Telegram ID {telegram_id} not found.")
                    return None
            except Exception as e:
                logger.error(f"Error getting user data from Redis: {e}")
                return None
        else:
            logger.error("No connection to Redis.")
            return None

    def update_user_password(self, telegram_id: str, password: str) -> bool:
        """
        Метод для обновления пароля пользователя в Redis.

        Аргументы:
        - telegram_id: ID пользователя в Telegram, пароль которого необходимо обновить.
        - password: новый пароль пользователя.

        Возвращает True, если пароль успешно обновлен в Redis, и False в противном случае.
        """
        if self.db:
            try:
                key = f"user:{telegram_id}"
                self.db.hset(key, mapping={'password': str(password)})
                logger.info(f"The password of the user with Telegram ID {telegram_id} was successfully updated in Redis.")
                return True
            except Exception as e:
                logger.error(f"Error updating user password in Redis: {e}")
                return False
        else:
            logger.error("No connection to Redis.")
            return False

    def update_user_status(self, telegram_id: str, online_status: int) -> bool:
        """
        Метод для обновления статуса пользователя в Redis.

        Аргументы:
        - telegram_id: ID пользователя в Telegram, статус которого необходимо обновить.
        - online_status: новый статус пользователя (0 | False = offline, 1 | True = online).

        Возвращает True, если статус успешно обновлен в Redis, и False в противном случае.
        """
        if self.db:
            try:
                key = f"user:{telegram_id}"
                self.db.hset(key, mapping={'online_status': str(int(online_status))})
                logger.info(f"The status of the user with Telegram ID {telegram_id} was successfully updated in Redis.")
                return True
            except Exception as e:
                logger.error(f"Error updating user status in Redis: {e}")
                return False
        else:
            logger.error("No connection to Redis.")
            return False

    def delete_user_data(self, telegram_id: str) -> bool:
        """
        Метод для удаления данных пользователя из Redis по Telegram ID.

        Аргументы:
        - telegram_id: ID пользователя в Telegram, данные которого нужно удалить.

        Возвращает True, если данные успешно удалены из Redis, и False в противном случае.
        """
        if self.db:
            try:
                key = f"user:{telegram_id}"
                result = self.db.delete(key)
                if result:
                    logger.info(f"User data with Telegram ID {telegram_id} has been successfully deleted from Redis.")
                    return True
                else:
                    logger.warning(f"Error deleting user data from Redis. There is no data for Telegram ID {telegram_id}.")
                    return False
            except Exception as e:
                logger.error(f"Error deleting user data from Redis: {e}")
                return False
        else:
            logger.error("No connection to Redis.")
            return False

    def close(self):
        if self.db:
            self.db.close()
            logger.info("Redis has been closed.")


redis_manager = RedisManager()

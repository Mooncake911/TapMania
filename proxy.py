import requests

# Учетные данные для прокси
proxy_username = "*********"
proxy_password = "*******"

# Прокси-сервер
proxy_ip_port = "url:port"

# Настройки прокси
proxies = {
    "http": f"http://{proxy_username}:{proxy_password}@{proxy_ip_port}",
    "https": f"http://{proxy_username}:{proxy_password}@{proxy_ip_port}",
}

# Выполнение запроса через прокси
response = requests.get("http://example.com", proxies=proxies)

# Выводим содержимое страницы
print(response.text)


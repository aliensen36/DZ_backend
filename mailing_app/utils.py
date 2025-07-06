import requests
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SEND_MESSAGE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
SEND_PHOTO_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

def send_telegram_message(user_id, text, button_url=None, image=None):
    reply_markup = {}

    if button_url:
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "Перейти к мероприятию",
                        "web_app": {"url": button_url}
                    }
                ]
            ]
        }

    try:
        if image:
            # Если это file_id
            if isinstance(image, str):
                payload = {
                    "chat_id": user_id,
                    "caption": text,
                    "photo": image,
                    "reply_markup": reply_markup  # Кнопка для file_id
                }
                response = requests.post(SEND_PHOTO_URL, json=payload)
            else:
                # Если это изображение (например, из ImageField)
                files = {'photo': open(image.path, 'rb')}  # Используем путь к файлу
                payload = {
                    "chat_id": user_id,
                    "caption": text,
                    "reply_markup": reply_markup  # Кнопка для файла
                }
                response = requests.post(SEND_PHOTO_URL, data=payload, files=files)
                files['photo'].close()  # Закрываем файл после отправки
        else:
            payload = {
                "chat_id": user_id,
                "text": text,
                "parse_mode": "HTML",
                "reply_markup": reply_markup
            }
            response = requests.post(SEND_MESSAGE_URL, json=payload)

        print(f"Ответ Telegram: {response.status_code}, {response.text}")
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения Telegram: {e}")

# Остальной код (signal) остается без изменений
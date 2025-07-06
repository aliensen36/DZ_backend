import requests
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SEND_MESSAGE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send_telegram_message(user_id, text, button_url=None):
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

    payload = {
        "chat_id": user_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup,
    }

    try:
        response = requests.post(SEND_MESSAGE_URL, json=payload)
        print("Ответ Telegram:", response.status_code, response.text)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения Telegram: {e}")
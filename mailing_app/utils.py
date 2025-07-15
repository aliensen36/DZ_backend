import os
import json
import logging
import requests
from dotenv import load_dotenv, find_dotenv

# Настройка логирования
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv(find_dotenv())

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SEND_MESSAGE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
SEND_PHOTO_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

def send_telegram_message(user_id, text, buttons=None, image=None):
    """
    Отправляет сообщение или фото в Telegram с настраиваемыми инлайн-кнопками.

    Args:
        user_id (str or int): ID чата или пользователя в Telegram.
        text (str): Текст сообщения или подпись к фото.
        buttons (list, optional): Список инлайн-кнопок в формате [[{'text': str, 'callback_data': str}, ...], ...].
        image (django.db.models.fields.files.ImageField, optional): Объект ImageField.

    Returns:
        bool: True, если отправка успешна, False в случае ошибки.
    """
    reply_markup = {}
    if buttons:
        reply_markup = {"inline_keyboard": buttons}

    response = None
    try:
        if image and hasattr(image, 'path') and image.path:
            # Отправка фото из ImageField
            payload = {
                "chat_id": str(user_id),
                "caption": text,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(reply_markup) if reply_markup else None
            }
            files = {'photo': open(image.path, 'rb')}
            logger.info(f"Отправка фото в Telegram: chat_id={user_id}, file={image.path}")
            response = requests.post(SEND_PHOTO_URL, data=payload, files=files)
            files['photo'].close()
        else:
            # Отправка текстового сообщения
            payload = {
                "chat_id": str(user_id),
                "text": text,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(reply_markup) if reply_markup else None
            }
            logger.info(f"Отправка текстового сообщения в Telegram: chat_id={user_id}, text={text}")
            response = requests.post(SEND_MESSAGE_URL, json=payload)

        logger.info(f"Ответ Telegram API: status={response.status_code}, body={response.text}")
        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке сообщения Telegram: {e}, response={getattr(response, 'text', 'No response')}")
        return False
    except FileNotFoundError as e:
        logger.error(f"Файл изображения не найден: {e}, image={image}")
        return False
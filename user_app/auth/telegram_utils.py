import hmac
import hashlib
from urllib.parse import parse_qs
from time import time
import logging

logger = logging.getLogger(__name__)

def verify_telegram_init_data(init_data, bot_token):
    """
    Проверяет подлинность initData от Telegram.
    Возвращает True, если подпись валидна, и False в противном случае.
    Добавлены подробные логи для отладки мини-приложения.
    """
    try:
        logger.info(f"--- verify_telegram_init_data start ---")
        logger.info(f"Raw init_data received: {init_data}")

        params = parse_qs(init_data)
        received_hash = params.get("hash", [""])[0]

        if not received_hash:
            logger.error("Missing hash in initData")
            return False

        # Проверка времени auth_date (не старше 24 часов)
        auth_date = int(params.get("auth_date", [0])[0])
        current_time = time()
        logger.info(f"auth_date: {auth_date}, current_time: {current_time}, age: {current_time - auth_date}s")
        if current_time - auth_date > 86400:
            logger.error("initData is too old")
            return False

        # Формируем data_check_string
        params.pop("hash", None)
        data_check_string = "\n".join(
            f"{key}={params[key][0]}" for key in sorted(params.keys())
        )
        logger.info(f"data_check_string: {data_check_string}")

        # Создаём секретный ключ
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Вычисляем HMAC-SHA-256
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        logger.info(f"calculated_hash: {calculated_hash}, received_hash: {received_hash}")

        if calculated_hash != received_hash:
            logger.error("Invalid initData signature")
            return False

        logger.info("initData verification successful")
        logger.info(f"--- verify_telegram_init_data end ---")
        return True

    except Exception as e:
        logger.error(f"Error verifying initData: {e}", exc_info=True)
        return False

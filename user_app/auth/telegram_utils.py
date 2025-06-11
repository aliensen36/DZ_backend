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
    """
    try:
        params = parse_qs(init_data)
        received_hash = params.get("hash", [""])[0]
        if not received_hash:
            logger.error("Missing hash in initData")
            return False

        # Проверка времени auth_date (не старше 24 часов)
        auth_date = int(params.get("auth_date", [0])[0])
        if time() - auth_date > 86400:
            logger.error("initData is too old")
            return False

        # Формируем data_check_string
        params.pop("hash", None)
        data_check_string = "\n".join(
            f"{key}={params[key][0]}" for key in sorted(params.keys())
        )

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

        if calculated_hash != received_hash:
            logger.error("Invalid initData signature")
            return False
        logger.info("initData verification successful")
        return True
    except Exception as e:
        logger.error(f"Error verifying initData: {e}", exc_info=True)
        return False
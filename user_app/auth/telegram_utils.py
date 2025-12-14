import hmac
import hashlib
from urllib.parse import parse_qsl, unquote
from time import time
import logging

logger = logging.getLogger(__name__)

def verify_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """
    Проверяет подлинность initData от Telegram WebApp.
    Работает с URL-кодированными JSON-значениями.
    """
    try:
        logger.info("--- verify_telegram_init_data start ---")
        logger.info(f"Raw init_data received: {init_data}")

        # Разбираем параметры init_data корректно
        params = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = params.pop("hash", None)
        if not received_hash:
            logger.error("Missing hash in initData")
            return False

        # Проверяем возраст данных
        auth_date = int(params.get("auth_date", 0))
        age = time() - auth_date
        logger.info(f"auth_date={auth_date}, current_time={time()}, age={age}s")
        if age > 86400:  # older than 1 day
            logger.error("initData is too old")
            return False

        # URL-декодируем значения перед формированием строки
        data_check_list = []
        for key in sorted(params.keys()):
            value = unquote(params[key])
            data_check_list.append(f"{key}={value}")
        data_check_string = "\n".join(data_check_list)
        logger.info(f"data_check_string: {data_check_string}")

        # Секретный ключ для проверки
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Вычисляем хэш
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        logger.info(f"calculated_hash: {calculated_hash}")
        logger.info(f"received_hash:   {received_hash}")

        if calculated_hash != received_hash:
            logger.error("Hash mismatch")
            return False

        logger.info("initData verification successful")
        return True
    except Exception as e:
        logger.exception(f"Error verifying initData: {e}")
        return False

import hmac
import hashlib
from time import time
import logging
from urllib.parse import unquote

logger = logging.getLogger(__name__)

def verify_telegram_init_data(raw_init_data: bytes, bot_token: str) -> bool:
    """
    Проверяет подлинность initData от Telegram.
    raw_init_data - байты query string (request.query_string)
    bot_token - токен вашего бота
    """
    try:
        logger.info("--- verify_telegram_init_data start ---")
        logger.info(f"Raw init_data bytes: {raw_init_data}")

        # Преобразуем байты в строку без двойного декодирования
        init_data_str = raw_init_data.decode('utf-8')
        logger.info(f"Decoded init_data: {init_data_str}")

        # Разбираем вручную, чтобы сохранить точные значения
        params = {}
        for pair in init_data_str.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key] = value

        if 'hash' not in params:
            logger.error("Missing hash in initData")
            return False

        received_hash = params.pop('hash')
        logger.info(f"Received hash: {received_hash}")

        # Проверка auth_date
        auth_date = int(params.get('auth_date', '0'))
        age = time() - auth_date
        logger.info(f"auth_date: {auth_date}, current_time: {time()}, age: {age}s")
        if age > 86400:
            logger.error("initData is too old")
            return False

        # Сортируем ключи и формируем data_check_string строго по Telegram спецификации
        data_check_string = '\n'.join(f"{k}={params[k]}" for k in sorted(params.keys()))
        logger.info(f"data_check_string: {data_check_string}")

        # Telegram WebApp HMAC-SHA256
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        logger.info(f"Calculated hash: {calculated_hash}")

        if calculated_hash != received_hash:
            for i, (c, r) in enumerate(zip(calculated_hash, received_hash)):
                if c != r:
                    logger.error(f"Hash mismatch at position {i}: calculated={c}, received={r}")
            return False

        logger.info("initData verification successful")
        return True

    except Exception as e:
        logger.error(f"Error verifying initData: {e}", exc_info=True)
        return False

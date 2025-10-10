from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO

def validate_image(image,
                   min_width=1024, min_height=512,
                   max_width=1280, max_height=720,
                   max_file_size_mb=10):
    """Проверка размеров изображения и веса файла (без использования .path)"""
    max_file_size = max_file_size_mb * 1024 * 1024
    if image.size > max_file_size:
        raise ValidationError(
            f"Максимальный размер файла {max_file_size_mb} MB. "
            f"Ваш файл: {image.size / (1024 * 1024):.2f} MB."
        )

    try:
        # Читаем файл из памяти
        image.seek(0)  # на случай повторного чтения
        img_bytes = BytesIO(image.read())
        img = Image.open(img_bytes)
        width, height = img.size
    except Exception as e:
        raise ValidationError(f"Ошибка при открытии изображения: {e}")

    if width > max_width or height > max_height:
        raise ValidationError(
            f"Максимальный размер {max_width}x{max_height}px. "
            f"Ваш файл: {width}x{height}px."
        )
    if width < min_width or height < min_height:
        raise ValidationError(
            f"Минимальный размер {min_width}x{min_height}px. "
            f"Ваш файл: {width}x{height}px."
        )

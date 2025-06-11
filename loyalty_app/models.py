from django.db import models
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import random
import string
import os
from django.contrib.auth import get_user_model

User = get_user_model()



class LoyaltyCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty_card', verbose_name='Пользователь')
    card_number = models.CharField(max_length=15, unique=True, editable=False, verbose_name='Номер карты')
    card_image = models.ImageField(upload_to='loyalty_cards/', blank=True, verbose_name='Изображение карты')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Карта лояльности'
        verbose_name_plural = 'Карты лояльности'

    def __str__(self):
        return f'Карта {self.card_number} ({self.user})'

    def generate_card_number(self):
        while True:
            number = ''.join(random.choices(string.digits, k=12))
            formatted_number = '-'.join([number[i:i + 3] for i in range(0, 12, 3)])
            if not LoyaltyCard.objects.filter(card_number=formatted_number).exists():
                return formatted_number

    def generate_card_image(self):
        if not self.user:
            raise ValueError("Cannot generate card image without a user")
        img = Image.new('RGB', (800, 500), color=(20, 60, 110))
        draw = ImageDraw.Draw(img)
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'arial.ttf')
            font_large = ImageFont.truetype(font_path, 40)
            font_medium = ImageFont.truetype(font_path, 30)
            font_small = ImageFont.truetype(font_path, 25)
        except Exception:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        first_name = self.user.user_first_name or self.user.first_name or "Не указано"
        last_name = self.user.user_last_name or self.user.last_name or "Не указано"
        draw.text((50, 100), "Карта лояльности", font=font_large, fill=(255, 255, 255))
        draw.text((50, 200), f"Имя: {first_name}", font=font_medium, fill=(255, 255, 255))
        draw.text((50, 250), f"Фамилия: {last_name}", font=font_medium, fill=(255, 255, 255))
        draw.text((50, 300), f"Номер карты: {self.card_number}", font=font_medium, fill=(255, 255, 255))

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        self.card_image.save(
            f'loyalty_card_{self.card_number}.png',
            ContentFile(buffer.getvalue()),
            save=False
        )
        buffer.close()

    def save(self, *args, **kwargs):
        if not self.card_number:
            self.card_number = self.generate_card_number()
        if not self.card_image or not self.pk:
            self.generate_card_image()
        super().save(*args, **kwargs)

import barcode
from barcode import Code128
from barcode.writer import ImageWriter
from django.db import models
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import random
import string
import os
from django.contrib.auth import get_user_model

from dzavod import settings
from resident_app.models import Resident

User = get_user_model()


class LoyaltyCard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty_card', verbose_name='Пользователь')
    card_number = models.CharField(max_length=15, unique=True, editable=False, verbose_name='Номер карты')
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

        cream_light = (255, 255, 230)
        img = Image.new('RGB', (800, 500), color=cream_light)
        draw = ImageDraw.Draw(img)

        try:
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Roboto_Condensed-Light.ttf')
            font_bold_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Roboto_Condensed-Bold.ttf')
            font_large = ImageFont.truetype(font_path, 40)
            font_medium = ImageFont.truetype(font_path, 30)
            font_medium_bold = ImageFont.truetype(font_bold_path, 30)
            font_small = ImageFont.truetype(font_path, 25)
        except Exception:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_medium_bold = ImageFont.load_default()
            font_small = ImageFont.load_default()

        logo_path = os.path.join(settings.MEDIA_ROOT, 'loyalty_cards', 'logo.png')

        logo_y = 20
        logo_x = 30
        logo_height = 0
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((150, 150), Image.Resampling.LANCZOS)
            logo_height = logo.height
            img.paste(logo, (logo_x, logo_y), logo)
        else:
            print(f"Логотип не найден по пути: {logo_path}")

        first_name = getattr(self.user, 'user_first_name', None) or getattr(self.user, 'first_name', 'Не указано')
        last_name = getattr(self.user, 'user_last_name', None) or getattr(self.user, 'last_name', 'Не указано')
        balance = self.get_balance()

        logo_title_spacing = 50
        title_text = "Карта лояльности"
        bbox_title = draw.textbbox((0, 0), title_text, font=font_large)
        title_width = bbox_title[2] - bbox_title[0]
        title_x = (img.width - title_width) // 2
        title_y = logo_y + logo_height + logo_title_spacing
        draw.text((title_x, title_y), title_text, font=font_large, fill=(0, 0, 0))

        title_spacing = 50
        base_y = title_y + bbox_title[3] - bbox_title[1] + title_spacing

        full_name = f"{first_name} {last_name}"
        line_spacing = 50
        draw.text((50, base_y), full_name, font=font_medium, fill=(0, 0, 0))

        bbox_name = draw.textbbox((0, 0), full_name, font=font_medium)
        name_height = bbox_name[3] - bbox_name[1]
        base_y += name_height + line_spacing

        # Баланс
        balance_prefix = "Баланс: "
        balance_suffix = " баллов"
        x_pos = 50

        draw.text((x_pos, base_y), balance_prefix, font=font_medium, fill=(0, 0, 0))
        prefix_width = draw.textbbox((0, 0), balance_prefix, font=font_medium)[2]
        draw.text((x_pos + prefix_width, base_y), str(balance), font=font_medium_bold, fill=(0, 0, 0))
        balance_width = draw.textbbox((0, 0), str(balance), font=font_medium_bold)[2]
        draw.text((x_pos + prefix_width + balance_width, base_y), balance_suffix, font=font_medium, fill=(0, 0, 0))

        # Штрихкод
        card_number_clean = self.card_number.replace('-', '')
        barcode_obj = Code128(card_number_clean, writer=ImageWriter())
        barcode_buffer = BytesIO()
        barcode_obj.write(barcode_buffer)
        barcode_buffer.seek(0)
        barcode_img = Image.open(barcode_buffer).convert("RGBA")

        barcode_x = (img.width - barcode_img.width) // 2
        barcode_y = 370
        img.paste(barcode_img, (barcode_x, barcode_y), barcode_img)

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer


    def save(self, *args, **kwargs):
        if not self.card_number:
            self.card_number = self.generate_card_number()
        super().save(*args, **kwargs)

    def get_balance(self):
        return self.transactions.aggregate(total=models.Sum('points'))['total'] or 0


TRANSACTION_TYPE =[
    ('начисление', 'начисление'),
    ('списание', 'списание')
]

class PointsTransaction(models.Model):
    points = models.IntegerField(null=False, verbose_name='Баллы (-/+): списание или пополнение')
    price = models.FloatField(null=False, verbose_name='Сумма с которой начислились баллы или списались')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE, verbose_name='Тип транзакции')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата транзакции')

    card_id = models.ForeignKey(LoyaltyCard, on_delete=models.CASCADE, related_name='transactions')
    resident_id = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='transactions')

    class Meta:
        verbose_name = 'Транзакция баллов'
        verbose_name_plural = 'Транзакции баллов'

    def __str__(self):
        return f"{self.transaction_type.capitalize()} {self.points} баллов"
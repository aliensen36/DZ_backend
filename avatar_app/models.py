from django.db import models
from user_app.models import User


class Avatar(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя аватара')
    description = models.TextField(verbose_name='Описание аватара')

    class Meta:
        verbose_name = 'Аватар'
        verbose_name_plural = 'Аватары'

    def __str__(self):
        return self.name


class Stage(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название стадии')
    description = models.TextField(verbose_name='Описание стадии')
    required_spending = models.PositiveIntegerField(default=0, verbose_name='Требуемая сумма трат')

    class Meta:
        ordering = ['required_spending']
        verbose_name = 'Стадия'
        verbose_name_plural = 'Стадии'

    def __str__(self):
        return self.name


class AvatarStage(models.Model):
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='avatar_stages', verbose_name='Аватар')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='avatar_stages', verbose_name='Стадия')
    default_img = models.ImageField(upload_to='avatars/photos/', verbose_name='Изображение')
    
    class Meta:
        unique_together = ('avatar', 'stage')
        verbose_name = 'Стадия конкретного аватара'
        verbose_name_plural = 'Стадии конкретных аватаров'

    def __str__(self):
        return f"{self.avatar.name} — {self.stage.name}"


class Animation(models.Model):
    avatar_stage = models.ForeignKey(AvatarStage, on_delete=models.CASCADE, related_name='animations', verbose_name='Стадия аватара')
    gif = models.ImageField(upload_to='avatars/gif/', verbose_name='GIF-анимация')

    class Meta:
        verbose_name = 'Анимация аватара'
        verbose_name_plural = 'Анимации аватаров'

    def __str__(self):
        return f"GIF {self.id} — {self.avatar_stage}"


class UserAvatarProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avatar_progress', verbose_name='Пользователь')
    avatar = models.ForeignKey('Avatar', on_delete=models.CASCADE, related_name='avatar_progress', verbose_name='Аватар')
    current_stage = models.ForeignKey('Stage', on_delete=models.CASCADE, related_name='avatar_progress', verbose_name='Стадия аватара')
    total_spending = models.PositiveIntegerField(default=0)
    current_outfit = models.ForeignKey('AvatarOutfit', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Надетая одежда')
    is_active = models.BooleanField(default=False, verbose_name='Текущий выбранный аватар')

    class Meta:
        unique_together = ('user', 'avatar')
        verbose_name = 'Прогресс пользователя'
        verbose_name_plural = 'Прогрессы пользователей'

    def __str__(self):
        return f"{self.user} → {self.avatar.name} ({self.current_stage.name})"
    
    def get_current_image(self):
        if self.current_outfit and self.current_outfit.custom_img:
            return self.current_outfit.custom_img.url
        avatar_stage = AvatarStage.objects.filter(avatar=self.avatar, stage=self.current_stage).first()
        return avatar_stage.default_img.url if avatar_stage else None
    
    def check_for_upgrade(self):
        """
        Проверяет, нужно ли перевести аватар на следующую стадию
        и переводит, если required_spending достигнут.
        """
        next_stage = (
            Stage.objects
            .filter(required_spending__gt=self.current_stage.required_spending)
            .order_by('required_spending')
            .first()
        )

        if next_stage and self.total_spending >= next_stage.required_spending:
            self.current_stage = next_stage
            self.save()
    

class AvatarOutfit(models.Model):
    avatar_stage = models.ForeignKey(AvatarStage, on_delete=models.CASCADE, related_name='outfits', verbose_name='Стадия аватара')
    outfit = models.ImageField(upload_to='avatars/clothes/previews/', verbose_name='Картинка комплекта (только одежда)')
    price = models.PositiveIntegerField(verbose_name='Цена (в баллах)')
    custom_img = models.ImageField(upload_to='avatars/clothes/avatar_images/', verbose_name='Картинка аватара в этой одежде')
    custom_animations = models.ManyToManyField('Animation', blank=True,verbose_name='Анимации аватара в одежде')

    class Meta:
        verbose_name = 'Одежда для аватара'
        verbose_name_plural = 'Одежда для аватаров'

    def __str__(self):
        return f"Одежда #{self.id} для {self.avatar_stage} за {self.price} баллов"
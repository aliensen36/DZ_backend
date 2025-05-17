from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, tg_id, password=None, **extra_fields):
        """
            Создание и сохранение юзера через tg id.
        """
        if not tg_id:
            raise ValueError("The Telegram ID must be set")

        user = self.model(tg_id=tg_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, tg_id, password=None, **extra_fields):
        """
            Создание суперюзера.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Superusers must have a password.")

        try:
            # Пытаемся найти существующего пользователя
            user = self.get(tg_id=tg_id)

            # Если пользователь найден, обновляем его права
            if not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.set_password(password)
                user.save(using=self._db)
                return user
            else:
                raise ValueError(f"Пользователь с TG_ID {tg_id} уже является суперпользователем")

        except self.model.DoesNotExist:
            # Если пользователь не найден, создаем нового
            return self.create_user(
                tg_id=tg_id,
                password=password,
                **extra_fields
            )

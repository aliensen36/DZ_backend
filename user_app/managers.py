from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, tg_id, password=None, **extra_fields):
        """
            Создание и сохранение юзера через tg id.
        """
        if not tg_id:
            raise ValueError("The Telegram ID must be set")

        user = self.model(tg_id=tg_id, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(self, tg_id, password=None, **extra_fields):
        """
            Создание суперюзера.
        """
        extra_fields.setdefault('role', 'design_admin')
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Superusers must have a password.")

        return self.create_user(tg_id=tg_id, password=password, **extra_fields)

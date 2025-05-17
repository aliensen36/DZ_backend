from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from getpass import getpass


class Command(BaseCommand):
    help = 'Создать суперюзера или обновить существующего до суперюзера'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        tg_id = input("TG_ID: ")
        try:
            tg_id = int(tg_id)
        except ValueError:
            self.stderr.write("TG_ID должен быть числом.")
            return

        password = getpass("Password: ")
        password2 = getpass("Password (again): ")

        if password != password2:
            self.stderr.write("Пароли не совпадают.")
            return

        try:
            user = User.objects.get(tg_id=tg_id)
            self.stdout.write(f"Пользователь с TG_ID {tg_id} уже существует. Обновляем до суперюзера...")
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            self.stdout.write(f"Создаём нового суперюзера с TG_ID {tg_id}...")
            User.objects.create_superuser(tg_id=tg_id, password=password)

        self.stdout.write(self.style.SUCCESS("Готово."))

import os
from uuid import uuid4
from dotenv import load_dotenv, find_dotenv
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from supabase import create_client

load_dotenv(find_dotenv())

class SupabaseStorage(Storage):
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.bucket_name = os.getenv('SUPABASE_BUCKET')

        if not all([self.supabase_url, self.supabase_key, self.bucket_name]):
            raise ValueError("SUPABASE_URL, SUPABASE_KEY или SUPABASE_BUCKET не определены в .env")

        self.client = create_client(self.supabase_url, self.supabase_key)

    def _save(self, name, content):
        content.seek(0)
        data = content.read()
        filename = f"{uuid4().hex}_{name}"
        print(f"[SupabaseStorage] Загружаем файл {filename} в bucket {self.bucket_name}")
        try:
            self.client.storage.from_(self.bucket_name).upload(
                path=filename,
                file=data,
                file_options={"content-type": content.content_type or "application/octet-stream"}
            )
            print(f"[SupabaseStorage] Успешно загружено {filename}")
        except Exception as e:
            print(f"[SupabaseStorage] Ошибка: {e}")
            raise e
        return filename

    def _open(self, name, mode='rb'):
        try:
            response = self.client.storage.from_(self.bucket_name).download(name)
            print(f"[SupabaseStorage] Открываем файл {name}")
            return ContentFile(response)
        except Exception as e:
            print(f"[SupabaseStorage] Ошибка открытия файла {name}: {e}")
            raise e

    def exists(self, name):
        try:
            self.client.storage.from_(self.bucket_name).get_public_url(name)
            print(f"[SupabaseStorage] Файл {name} существует")
            return True
        except Exception as e:
            print(f"[SupabaseStorage] Файл {name} не существует: {e}")
            return False

    def url(self, name):
        print(f"[SupabaseStorage] Генерируем URL для {name}")
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"

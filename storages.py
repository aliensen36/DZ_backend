import os
from uuid import uuid4
from dotenv import load_dotenv, find_dotenv
from django.core.files.storage import Storage
from supabase import create_client

# Загружаем переменные из .env
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

        # Генерируем уникальное имя файла
        filename = f"{uuid4().hex}_{name}"

        # Загружаем файл в Supabase Storage
        try:
            self.client.storage.from_(self.bucket_name).upload(filename, data)
        except Exception as e:
            print(f"Ошибка при загрузке файла в Supabase: {e}")
            raise e

        return filename

    def url(self, name):
        # Возвращаем публичный URL
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"

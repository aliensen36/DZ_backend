import os
from django.core.files.storage import Storage
from supabase import create_client

class SupabaseStorage(Storage):
    def __init__(self):
        self.url = os.environ['SUPABASE_URL']
        self.key = os.environ['SUPABASE_KEY']
        self.bucket_name = os.environ['SUPABASE_BUCKET']
        self.client = create_client(self.url, self.key)

    def _save(self, name, content):
        # Загружаем файл в Supabase Storage
        data = content.read()
        self.client.storage.from_(self.bucket_name).upload(name, data)
        return name

    def url(self, name):
        # Возвращаем публичный URL
        return f"{self.url}/storage/v1/object/public/{self.bucket_name}/{name}"

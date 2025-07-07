FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN mkdir -p /app/media/loyalty_cards

CMD ["sh", "-c", "\
    python manage.py migrate loyalty_app zero || echo 'No migrations to rollback'; \
    python manage.py migrate resident_app zero || echo 'No migrations to rollback'; \
    python manage.py makemigrations; \
    python manage.py migrate; \
    python manage.py runserver 0.0.0.0:8000 \
"]

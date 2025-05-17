# Телеграм мини апп Дизайн завода

## 📋 Функциональность

- **Редактировать**: редактировать.

---

## 🛠️ Установка и запуск проекта

### Шаг 1: Клонировать репозиторий
```bash
# Clone with HTTPS
git clone https://github.com/...git
```

### Шаг 2: Создать виртуальное окружение
```bash
python -m venv venv
venv\Scripts\activate
```

### Шаг 3: Установить зависимости
```bash
pip install -r requirements.txt # Установка из файла
python -m pip freeze > requirements.txt # Обновление списка зависимостей
```

### Шаг 4: Заполнить файл .env по образцу из .env.example

### Шаг 5: Запустить сервер
```bash
python manage.py runserver
```

### Миграции
```bash
python manage.py makemigrations

python manage.py migrate
```

### Суперпользователь
```bash
python manage.py createsuperuser_or_promote
```

### 🛠️ Технологии

- **Backend**: Python, DRF 
- **База данных**:   SQLite, PostgreSQL
- **Язык программирования**: Python 3.10+  
- **Контейнеризация**: Docker
- **Документация API**: OpenAPI  


### 📄 Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. в LICENSE.

### 📧 Контакты
Если у вас есть вопросы или предложения, вы можете связаться с разработчиками:

Email: 
GitHub:

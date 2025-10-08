import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
import dj_database_url

load_dotenv(find_dotenv())

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

BOT_API_KEY = os.getenv('BOT_API_KEY')

TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '158.160.25.8',
    '127.0.0.1',
    "backend_django_container", 
    'back.design-zavod.tech',
    'www.back.design-zavod.tech',
    'design-zavod.tech',
    'www.design-zavod.tech',
] + os.getenv('ALLOWED_HOSTS', '').split()

# Основные доверенные origins (бек и фронт)
BASE_CORS_ALLOWED_ORIGINS = [
    'https://back.design-zavod.tech',
    'https://design-zavod.tech',
    'http://localhost:5173',  # Для тестирования фронта, потом убрать 
]

FRONTEND_BASE_URL = "https://design-zavod.tech"

# Динамические origins из переменной окружения
ENV_CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]

# Объединенный список
CORS_ALLOWED_ORIGINS = BASE_CORS_ALLOWED_ORIGINS + ENV_CORS_ALLOWED_ORIGINS

CORS_ALLOW_HEADERS = ["authorization",
                      "content-type",
                      "x-api-key",
                      ]

CORS_ALLOW_CREDENTIALS = True

SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'django_celery_beat',

    'user_app.apps.UserAppConfig',
    'mailing_app.apps.MailingAppConfig',
    'loyalty_app.apps.LoyaltyAppConfig',
    'resident_app.apps.ResidentAppConfig',
    'event_app.apps.EventAppConfig',
    'faq_app.apps.FaqAppConfig',
    'avatar_app.apps.AvatarAppConfig',
    'route_app.apps.RouteAppConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dzavod.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dzavod.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.environ.get('DATABASE_URL'),
#         conn_max_age=600,
#         ssl_require=True
#     )
# }



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru'

LANGUAGES = [
    ('ru', 'русский'),
    ('en-us', 'english')
]

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'user_app.User'

REST_FRAMEWORK = {        
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema', 
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'user_app.auth.authentication.CustomJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


SPECTACULAR_SETTINGS = {
    "TITLE": "DZAVOD API",
    "VERSION": "0.0.1",
    "SERVE_INCLUDE_SCHEMA": False,

    "SWAGGER_UI_SETTINGS": {
        "filter": True,
        "persistAuthorization": True,
    },

    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX_TRIM": True,
    "TAGS_SORTER": "alpha",
    "OPERATIONS_SORTER": "alpha",
    "TAGS": [
        {"name": "Пользователи", "description": "Управление пользователями"},
        {"name": "Маршруты", "description": "Работа с картой"},
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'user_app': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


CSRF_TRUSTED_ORIGINS = [
    'https://back.design-zavod.tech',
    'https://design-zavod.tech'
]

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
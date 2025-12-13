import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
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
# DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '158.160.25.8',
    '127.0.0.1',
    "backend_django_container", 
    'frontend-tau-fawn-68.vercel.app',
    '89.111.141.219',
    'aliensen.online',
    'api.aliensen.online',
    'www.aliensen.online',
]
# ] + os.getenv('ALLOWED_HOSTS', '').split()

# Основные доверенные origins (бек и фронт)
CORS_ALLOWED_ORIGINS = [
    'https://frontend-tau-fawn-68.vercel.app',
    'http://localhost:5173',
]

# FRONTEND_BASE_URL = "https://design-zavod.tech"
FRONTEND_BASE_URL = 'https://frontend-tau-fawn-68.vercel.app/'

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
    'storages',

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
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


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
    'root': {  # добавляем корневой логгер
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {  # чтобы видеть общие логи Django
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'user_app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'SupabaseStorage': {  # добавляем наш кастомный логгер
            'handlers': ['console'],
            'level': 'DEBUG',  # можно временно поставить DEBUG для детальной информации
            'propagate': True,
        },
    },
}



CSRF_TRUSTED_ORIGINS = [
    'https://aliensen.online',
    'https://www.aliensen.online',
]
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True


CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')

WHITENOISE_MANIFEST_STRICT = False

AWS_ACCESS_KEY_ID = os.environ.get('SUPABASE_S3_ACCESS_KEY_ID')  # S3 Access Key
AWS_SECRET_ACCESS_KEY = os.environ.get('SUPABASE_S3_SECRET_ACCESS_KEY')  # S3 Secret Key
AWS_STORAGE_BUCKET_NAME = os.environ.get('SUPABASE_S3_BUCKET_NAME')  # Имя бакета
AWS_S3_REGION_NAME = os.environ.get('SUPABASE_S3_REGION_NAME', 'us-east-1')  # Регион
AWS_S3_ENDPOINT_URL = os.environ.get('SUPABASE_S3_ENDPOINT_URL')  # Endpoint URL

# Настройки хранилища
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'access_key': AWS_ACCESS_KEY_ID,
            'secret_key': AWS_SECRET_ACCESS_KEY,
            'bucket_name': AWS_STORAGE_BUCKET_NAME,
            'region_name': AWS_S3_REGION_NAME,
            'endpoint_url': AWS_S3_ENDPOINT_URL,
        },
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# URL для медиафайлов
# MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
MEDIA_URL = 'https://nnpvsgtcvnyrxrbtzumz.supabase.co/storage/v1/object/public/media/'

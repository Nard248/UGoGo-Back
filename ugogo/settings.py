import certifi
import environ
import os
from datetime import timedelta
from pathlib import Path
from corsheaders.defaults import default_headers



BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env.test'))

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['SENDGRID_API_KEY'] = "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"


# Build paths inside the project like this: BASE_DIR / 'subdir'.

# Secret key and debug settings
SECRET_KEY = 'django-insecure-&b)b9=ldmzq6p%v7myop3d+g8=a9pwm$^j0p1+6rhmn#l^^zft'
DEBUG = True

ALLOWED_HOSTS = ['ugogo-auhdbad8drdma7f6.canadacentral-01.azurewebsites.net', '127.0.0.1', '0.0.0.0', 'localhost',
                 "192.168.11.52", "192.168.11.72", "192.168.200.249", "192.168.11.55", '192.168.5.53']

AUTH_USER_MODEL = 'users.Users'

CSRF_TRUSTED_ORIGINS = [
    "https://ugogo-auhdbad8drdma7f6.canadacentral-01.azurewebsites.net",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'drf_yasg',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'users',
    'offers',
    'items',
    'locations',
    'core',
    'flight_requests',
    'django_filters',
    'corsheaders',
    'azure_storage_handler',
    'allauth.socialaccount.providers.google',
    "channels",
    "chat",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ugogo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ugogo.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ugogo_db',
        'USER': 'ugogo_admin',
        'PASSWORD': 'FCxV3VrZvUCg6QgA',
        'HOST': 'ugogo.postgres.database.azure.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'PASSWORD': '1234',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        },
    },
    'USE_SESSION_AUTH': False,
}

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Simple JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # Use the Django SECRET_KEY
}


CORS_ALLOWED_ORIGINS = [
    'http://192.168.11.52:8000',
    'http://localhost:3000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0',
    'http://192.168.11.70',
    'http://localhost:3000',
    'http://192.168.184.180:3000',
    'http://192.168.11.54:3000'
]


CORS_ALLOW_HEADERS = list(default_headers) + [
    "Authorization",
    "Content-Type",
    "X-CSRFToken",
]

CORS_ALLOW_CREDENTIALS = True

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False


AZURE_ACCOUNT_NAME = env("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = "OzYwtxC4bkYddPUKGNX9tTxvAnwZUupkeXcYfQAaB/VvLeXw5TBdlGOnhZn34wjnbfUg8O+cEQTO+AStXUOuhA=="
AZURE_ITEM_IMAGE_CONTAINER = env("AZURE_ITEM_IMAGE_CONTAINER")
AZURE_ITEM_CATEGORY_LOGO_CONTAINER = env("AZURE_ITEM_CATEGORY_LOGO_CONTAINER")
AZURE_USER_PASSPORT_IMAGE_CONTAINER = env("AZURE_USER_PASSPORT_IMAGE_CONTAINER")

EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

STRIPE_SECRET_KEY = 'sk_test_51R81HEQLU3iCaOMisS0uyjCjDGdEaKRKX0tDTC79dQgHoPORR5988ZHdH9nqgehwItqzUVVnHzXgOCzk8wEQv1ai00qv65ADrD'
STRIPE_PUBLISHABLE_KEY = 'pk_test_51R81HEQLU3iCaOMia0ZMyCk7NcuTvwfM0Oq0I0AtYBxPBAGZw4SIXD2FPTcCTWRiGemsRXGHU9EdFVeu72Y3Pw2F00noUUc9tZ'

ASGI_APPLICATION = "yourproject.asgi.application"

DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_USE_SSL = os.getenv("REDIS_USE_SSL", "false").lower() == "true"

REDIS_SCHEME = "rediss" if REDIS_USE_SSL else "redis"
REDIS_URL = f"{REDIS_SCHEME}://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
            # Azure TLS: disable cert validation if you don't supply CA bundle
            # (Prefer proper CA validation in production)
            "ssl": {"cert_reqs": 0} if REDIS_USE_SSL else None,
        },
    }
}
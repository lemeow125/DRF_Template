from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv, find_dotenv  # Python dotenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Backend folder (/backend)
BASE_DIR = Path(__file__).resolve().parent.parent
# Root folder where docker-compose.yml is located
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# If you're hosting this with a secret provider, have this set to True
USE_VAULT = bool(os.getenv('USE_VAULT', False) == 'True')
# Have this set to True to serve media and static contents directly via Django
SERVE_MEDIA = bool(os.getenv('SERVE_MEDIA', False) == 'True')

load_dotenv(find_dotenv())


def get_secret(secret_name):
    if USE_VAULT:
        try:
            pass
            # Add specific implementations here if deploying to Azure, GCP, or AWS to get secrets from vault
        except:
            secret_value = ""
    else:
        # Fallback to .env or system environment variables for local development
        secret_value = os.getenv(secret_name)

    if secret_value is None:
        raise ValueError(f"Secret '{secret_name}' not found.")
    else:
        return secret_value


# URL Prefixes
URL_SCHEME = 'https' if (get_secret('USE_HTTPS') == 'True') else 'http'
# Backend
BACKEND_ADDRESS = get_secret('BACKEND_ADDRESS')
BACKEND_PORT = get_secret('BACKEND_PORT')
# Frontend
FRONTEND_ADDRESS = get_secret('FRONTEND_ADDRESS')
FRONTEND_PORT = get_secret('FRONTEND_PORT')

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    # Frontend
    f'{URL_SCHEME}://{FRONTEND_ADDRESS}:{FRONTEND_PORT}',
    f'{URL_SCHEME}://{FRONTEND_ADDRESS}',  # For external domains
    # Backend
    f'{URL_SCHEME}://{BACKEND_ADDRESS}:{BACKEND_PORT}',
    f'{URL_SCHEME}://{BACKEND_ADDRESS}'  # For external domains
    # You can also set up https://*.name.xyz for wildcards here
]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (get_secret('BACKEND_DEBUG') == 'True')
# Determines whether or not to insert test data within tables
SEED_DATA = (get_secret('SEED_DATA') == 'True')
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('SECRET_KEY')
# Selenium Config
# Initiate CAPTCHA solver in test mode
CAPTCHA_TESTING = (get_secret('CAPTCHA_TESTING') == 'True')
# If using Selenium and/or the provided CAPTCHA solver, determines whether or not to use proxies
USE_PROXY = (get_secret('USE_PROXY') == 'True')

# Stripe (For payments)
STRIPE_SECRET_KEY = get_secret(
    "STRIPE_SECRET_KEY")
STRIPE_SECRET_WEBHOOK = get_secret('STRIPE_SECRET_WEBHOOK')
STRIPE_CHECKOUT_URL = f''

# Email credentials
EMAIL_HOST = get_secret('EMAIL_HOST')
EMAIL_HOST_USER = get_secret('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')
EMAIL_PORT = get_secret('EMAIL_PORT')
EMAIL_USE_TLS = (get_secret('EMAIL_USE_TLS') == 'True')
EMAIL_ADDRESS = (get_secret('EMAIL_ADDRESS') == 'True')

# Application definition

INSTALLED_APPS = [
    'silk',
    'config',
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.simple_history',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'django_extensions',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_results',
    'django_celery_beat',
    'simple_history',
    'djoser',
    'corsheaders',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'webdriver',
    'accounts',
    'user_groups',
    'subscriptions',
    'payments',
    'billing',
    'emails',
    'notifications'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "silk.middleware.SilkyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

ROOT_URLCONF = 'config.urls'
if SERVE_MEDIA:
    # Cloud Storage Settings
    # This is assuming you use the same bucket for media and static containers
    CLOUD_BUCKET = get_secret('CLOUD_BUCKET')
    MEDIA_CONTAINER = get_secret('MEDIA_CONTAINER')
    STATIC_CONTAINER = get_secret('STATIC_CONTAINER')

    MEDIA_URL = f'https://{CLOUD_BUCKET}/{MEDIA_CONTAINER}/'
    MEDIA_ROOT = f'https://{CLOUD_BUCKET}/'

    STATIC_URL = f'https://{CLOUD_BUCKET}/{STATIC_CONTAINER}/'
    STATIC_ROOT = f'https://{CLOUD_BUCKET}/{STATIC_CONTAINER}/'

    # Consult django-storages documentation when filling in these values. This will vary depending on your cloud service provider
    STORAGES = {
        'default': {
            # TODO: Set this up here if you're using cloud storage
            'BACKEND': None,
            'OPTIONS': {
                # Optional parameters
            },
        },
        'staticfiles': {
            # TODO: Set this up here if you're using cloud storage
            'BACKEND': None,
            'OPTIONS': {
                # Optional parameters
            },
        },
    }
else:
    STATIC_URL = 'static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    MEDIA_URL = 'api/v1/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'emails/templates/',
        ],
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [

        'rest_framework.throttling.AnonRateThrottle',

        'rest_framework.throttling.UserRateThrottle'

    ],

    'DEFAULT_THROTTLE_RATES': {

        'anon': '360/min',

        'user': '1440/min'

    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# DRF-Spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'DRF-Template',
    'DESCRIPTION': 'A Template Project by Keannu Bernasol',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        # Set to True to avoid issues with pgbouncer when pooling connections
        'DISABLE_SERVER_SIDE_CURSORS': True,
        "NAME": get_secret("DB_DATABASE"),
        "USER": get_secret("DB_USERNAME"),
        "PASSWORD": get_secret("DB_PASSWORD"),
        "HOST": get_secret("DB_HOST"),
        "PORT": get_secret("DB_PORT"),
        "OPTIONS": {
            "sslmode": get_secret("DB_SSL_MODE")
        },
    }
}
# Django Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{get_secret('REDIS_HOST')}:{get_secret('REDIS_PORT')}/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

AUTH_USER_MODEL = 'accounts.CustomUser'

DJOSER = {
    'SEND_ACTIVATION_EMAIL': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'PASSWORD_RESET_CONFIRM_URL': 'reset_password_confirm/{uid}/{token}',
    'ACTIVATION_URL': 'activation/{uid}/{token}',
    'USER_AUTHENTICATION_RULES': ['djoser.authentication.TokenAuthenticationRule'],
    'EMAIL': {
        'activation': 'emails.templates.ActivationEmail',
        'password_reset': 'emails.templates.PasswordResetEmail'
    },
    'SERIALIZERS': {
        'user': 'accounts.serializers.CustomUserSerializer',
        'current_user': 'accounts.serializers.CustomUserSerializer',
        'user_create': 'accounts.serializers.UserRegistrationSerializer',
    },
    'PERMISSIONS': {
        # Disable some unneeded endpoints by setting them to admin only
        'username_reset': ['rest_framework.permissions.IsAdminUser'],
        'username_reset_confirm': ['rest_framework.permissions.IsAdminUser'],
        'set_username': ['rest_framework.permissions.IsAdminUser'],
        'set_password': ['rest_framework.permissions.IsAdminUser'],
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        "OPTIONS": {
            "min_length": 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    # Additional password validators
    {
        'NAME': 'accounts.validators.SpecialCharacterValidator',
    },
    {
        'NAME': 'accounts.validators.LowercaseValidator',
    },
    {
        'NAME': 'accounts.validators.UppercaseValidator',
    },
    {
        'NAME': 'accounts.validators.NumberValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = get_secret('TIMEZONE')

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_NAME = 'DRF-Template'

# JWT Token Lifetimes
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=3)
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
DJANGO_LOG_LEVEL = "DEBUG"
# Enables VS Code debugger to break on raised exceptions
DEBUG_PROPAGATE_EXCEPTIONS = "DEBUG"

# Celery Configuration Options
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = get_secret("CELERY_BROKER")
CELERY_BROKER = get_secret("CELERY_BROKER")
CELERY_BACKEND = get_secret("CELERY_BROKER")
CELERY_RESULT_BACKEND = get_secret("CELERY_RESULT_BACKEND")
CELERY_RESULT_EXTENDED = True

# Celery Beat Options
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Maximum number of rows that can be updated within the Django admin panel
DATA_UPLOAD_MAX_NUMBER_FIELDS = 20480

GRAPH_MODELS = {
    'app_labels': ['accounts', 'user_groups', 'billing', 'emails', 'payments', 'subscriptions']
}

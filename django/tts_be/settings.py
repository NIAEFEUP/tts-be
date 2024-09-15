"""
Django settings for tts_be project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os 
from dotenv import dotenv_values
# from university.auth import CustomOIDCAuthentationBackend


CONFIG={
    **dotenv_values(".env"),  # load variables
    **os.environ,  # override loaded values with environment variables
}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

SECRET_KEY = CONFIG['SECRET_KEY']

JWT_KEY= CONFIG['JWT_KEY']

DOMAIN = os.getenv('DOMAIN')
DEBUG = False if int(CONFIG['DEBUG']) == 0 else True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', 'tts.niaefeup.pt', 'tts-staging.niaefeup.pt', 'tts-dev.niaefeup.pt']

# Application definition

INSTALLED_APPS = [ 
    # 'django_extensions',
    'university',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions', # legacy
    'django.contrib.messages',
    'rest_framework', 
    'django.contrib.staticfiles',
    'mozilla_django_oidc'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'university.auth_middleware.AuthMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
    'django.middleware.csrf.CsrfViewMiddleware'
    #'djangosaml2.middleware.SamlSessionMiddleware'
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True

ROOT_URLCONF = 'tts_be.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'university/exchange/emails')
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



WSGI_APPLICATION = 'tts_be.wsgi.application'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'university.auth.CustomOIDCAuthentationBackend',
    # 'mozilla_django_oidc.auth.OIDCAuthenticationBackend'
    #'djangosaml2.backends.Saml2Backend'
)

OIDC_RP_CLIENT_ID = os.environ['OIDC_RP_CLIENT_ID']
OIDC_RP_CLIENT_SECRET = os.environ['OIDC_RP_CLIENT_SECRET']
OIDC_RP_SIGN_ALGO = "RS256"

OIDC_STORE_ID_TOKEN = True
OIDC_STORE_ACCESS_TOKEN = True

OIDC_OP_AUTHORIZATION_ENDPOINT = "https://open-id.up.pt/realms/sigarra/protocol/openid-connect/auth"
OIDC_OP_TOKEN_ENDPOINT = "https://open-id.up.pt/realms/sigarra/protocol/openid-connect/token"
OIDC_OP_USER_ENDPOINT = "https://open-id.up.pt/realms/sigarra/protocol/openid-connect/userinfo"
OIDC_OP_JWKS_ENDPOINT = "https://open-id.up.pt/realms/sigarra/protocol/openid-connect/certs"
OIDC_OP_LOGOUT_ENDPOINT = "https://open-id.up.pt/realms/sigarra/protocol/openid-connect/logout"

OIDC_RP_SCOPES = "openid email profile uporto_data"

LOGIN_REDIRECT_URL = "/"

# AUTH_USER_MODEL = 'university.TTSUser'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT') ,
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Api description
REST_FRAMEWORK = {
    # Setting default renderer.
    # https://www.django-rest-framework.org/api-guide/renderers/
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{CONFIG['TTS_REDIS_HOST']}:{CONFIG['TTS_REDIS_PORT']}//"
    }
}

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3100',
]
# CSRF_COOKIE_SECURE = False

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3100",
    "https://localhost:3100",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "X_CSRFTOKEN",
    "X-CSRFToken"
]

VERIFY_EXCHANGE_TOKEN_EXPIRATION_SECONDS = 3600 * 24

EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = ''

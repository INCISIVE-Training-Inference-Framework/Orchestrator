import json
import logging.config
import os
from pathlib import Path

import psycopg2.extensions

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django_insecure')
DEBUG = os.getenv('DEBUG', 'True')
if DEBUG.lower() in ('yes', 'true', 't', 'y', '1'):
    DEBUG = True
else:
    DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').split(',')

# Application definition

INSTALLED_APPS = [
    'main.apps.MainConfig',
    'rest_framework',
    'django_filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]
if not DEBUG:
    INSTALLED_APPS += ['django_apscheduler']
INSTALLED_APPS += ['django_cleanup.apps.CleanupConfig']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'orchestrator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'orchestrator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / '../storage/db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.{}'.format(os.getenv('DATABASE_ENGINE')),
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': os.getenv('DATABASE_USERNAME'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD'),
            'HOST': os.getenv('DATABASE_HOST'),
            'PORT': os.getenv('DATABASE_PORT'),
            'OPTIONS': {
                'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
            }
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.getenv('STATIC_ROOT', '/static/')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Rest framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'orchestrator.utils.StandardResultsSetPagination',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'orchestrator.utils.StandardResultsOrdering'
    ],
    'EXCEPTION_HANDLER': 'main.api.custom_exception_handler.custom_exception_handler',
}

# Files storage
MEDIA_ROOT = '../storage/files'
MEDIA_URL = '../storage/files/'

# Logging
if not DEBUG:
    # Clear prev config
    LOGGING_CONFIG = None

    # Get loglevel from env
    LOGLEVEL = os.getenv('LOGLEVEL', 'info').upper()

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
            },
        },
        'loggers': {
            '': {
                'level': LOGLEVEL,
                'handlers': ['console', ],
            },
        },
    })

# Domain
MAAS_API_HOSTNAME = os.getenv('MAAS_API_HOSTNAME', 'maas-service:8000')
ORCHESTRATOR_API_HOSTNAME = os.getenv('ORCHESTRATOR_API_HOSTNAME', 'orchestrator-service:8000')
AI_ENGINE_IMAGES_REGISTRY = os.getenv('AI_ENGINE_IMAGES_REGISTRY', 'localhost:5000')
COMPONENT_IMAGES_REGISTRY = os.getenv('COMPONENT_IMAGES_REGISTRY', 'localhost:5000')

VALID_DATA_PARTNERS = os.getenv('VALID_DATA_PARTNERS', 'data-partner-1,data-partner-2').split(',')
VALID_DATA_PARTNERS = set(VALID_DATA_PARTNERS)

VALID_AI_ENGINE_FUNCTIONALITIES = os.getenv('VALID_AI_ENGINE_FUNCTIONALITIES', 'training_from_scratch,'
                                                                               'training_from_pretrained_model,'
                                                                               'evaluating_from_pretrained_model,'
                                                                               'merging_models,'
                                                                               'inferencing_from_pretrained_model').split(',')
VALID_AI_ENGINE_FUNCTIONALITIES = set(VALID_AI_ENGINE_FUNCTIONALITIES)

VALIDATE_WITH_MAAS = os.getenv('VALIDATE_WITH_MAAS', 'false')
if VALIDATE_WITH_MAAS.lower() in ('yes', 'true', 't', 'y', '1'):
    VALIDATE_WITH_MAAS = True
else:
    VALIDATE_WITH_MAAS = False

PROCESSOR_RESOURCE_MANAGER_VERSION = os.getenv('PROCESSOR_RESOURCE_MANAGER_VERSION', '2.0.0')
PROCESSOR_RESOURCE_MANAGER_API_HOST = os.getenv('PROCESSOR_RESOURCE_MANAGER_API_HOST', '127.0.0.1:8000')
PROCESSOR_RESOURCE_MANAGER_CALLBACK_URL = os.getenv('PROCESSOR_RESOURCE_MANAGER_CALLBACK_URL', '/api/callback')

AI_ENGINE_PLATFORM_VARS_INPUT_ELEMENTS = os.getenv('AI_ENGINE_PLATFORM_VARS_INPUT_ELEMENTS', '/tmp/input_elements/')
AI_ENGINE_PLATFORM_VARS_INPUT_DATA_TRAINING = os.getenv('AI_ENGINE_PLATFORM_VARS_INPUT_DATA_TRAINING', '/tmp/input_elements/platform_data/')
AI_ENGINE_PLATFORM_VARS_INPUT_DATA_EVALUATION = os.getenv('AI_ENGINE_PLATFORM_VARS_INPUT_DATA_EVALUATION', '/tmp/input_elements/platform_data/')
AI_ENGINE_PLATFORM_VARS_INPUT_DATA_INFERENCE = os.getenv('AI_ENGINE_PLATFORM_VARS_INPUT_DATA_INFERENCE', '/tmp/input_elements/external_data/')
AI_ENGINE_PLATFORM_VARS_INPUT_AI_ELEMENTS = os.getenv('AI_ENGINE_PLATFORM_VARS_INPUT_AI_ELEMENTS', '/tmp/ai_elements/')
AI_ENGINE_PLATFORM_VARS_INPUT_USER_VARS = os.getenv('AI_ENGINE_PLATFORM_VARS_INPUT_USER_VARS', '/tmp/ai_elements/ai_engine_version_user_vars.json')
AI_ENGINE_PLATFORM_VARS_INPUT_MODEL = os.getenv('AI_ENGINE_PLATFORM_VARS_INPUT_MODEL', '/tmp/ai_elements/ai_model/')
AI_ENGINE_PLATFORM_VARS_INPUT_MODELS = os.getenv('AI_ENGINE_PLATFORM_VARS_INPUT_MODELS', '/tmp/ai_elements/ai_models/')
AI_ENGINE_PLATFORM_VARS_OUTPUT_ELEMENTS = os.getenv('AI_ENGINE_PLATFORM_VARS_OUTPUT_ELEMENTS', '/tmp/output_elements/')
AI_ENGINE_PLATFORM_VARS_OUTPUT_MODEL = os.getenv('AI_ENGINE_PLATFORM_VARS_OUTPUT_MODEL', '/tmp/output_elements/ai_model/')
AI_ENGINE_PLATFORM_VARS_OUTPUT_EVALUATION_METRICS = os.getenv('AI_ENGINE_PLATFORM_VARS_OUTPUT_EVALUATION_METRICS', '/tmp/output_elements/evaluation_metrics.json')
AI_ENGINE_PLATFORM_VARS_OUTPUT_INFERENCE_RESULTS = os.getenv('AI_ENGINE_PLATFORM_VARS_OUTPUT_INFERENCE_RESULTS', '/tmp/output_elements/generic_file/')
AI_ENGINE_PLATFORM_VARS_API_PING_URL = os.getenv('AI_ENGINE_PLATFORM_VARS_API_PING_URL', '/api/ping')
AI_ENGINE_PLATFORM_VARS_API_RUN_URL = os.getenv('AI_ENGINE_PLATFORM_VARS_API_RUN_URL', '/api/run')
AI_ENGINE_PLATFORM_VARS_API_HOST = os.getenv('AI_ENGINE_PLATFORM_VARS_API_HOST', '127.0.0.1:8001')

ARGO_WORKFLOWS_API_HOST = os.getenv('ARGO_WORKFLOWS_API_HOST', 'https://localhost:2746')
ARGO_WORKFLOWS_NAMESPACE = os.getenv('ARGO_WORKFLOWS_NAMESPACE', 'incisive-dev')

# tasks
UPDATE_STATUS_SECONDS_TIMER = int(os.getenv('UPDATE_STATUS_MINUTES_TIMER', 2))

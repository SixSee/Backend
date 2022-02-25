from .base import *

ALLOWED_HOSTS = env.ALLOWED_HOST
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.DB_NAME,
        'USER': env.DB_USER,
        'PASSWORD': env.DB_PASSWORD,
        'HOST': env.DB_HOST,
        'PORT': env.DB_PORT,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
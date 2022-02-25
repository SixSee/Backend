from .base import *

INSTALLED_APPS += [
    'drf_yasg',
"silk"
]
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]


SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
}
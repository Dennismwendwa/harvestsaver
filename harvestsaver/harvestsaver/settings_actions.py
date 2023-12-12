from .settings import *
DEBUG = False

YOUR_DOMAIN = "http://127.0.0.1:8000"
DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
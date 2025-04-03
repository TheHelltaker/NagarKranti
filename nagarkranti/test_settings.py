# test_settings.py
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'nagarkranti_test',
        'USER': 'postgres',
        'PASSWORD': 'sysadmin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Use a faster password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable throttling for testing
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # Inherit from your main settings
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {}
}

# Use in-memory file storage for tests to avoid leaving files
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

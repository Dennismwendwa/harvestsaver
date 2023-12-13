from .settings import *
DEBUG = True

YOUR_DOMAIN = "http://127.0.0.1:8000"
DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# AWS Bucket settings
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_SIGNATURE_NAME = os.environ.get("AWS_S3_SIGNATURE_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_S3_FILE_OVERWRITE = os.environ.get("AWS_S3_FILE_OVERWRITE")
AWS_DEFAULT_ACL = None
AWS_S3_VERITY = os.environ.get("AWS_S3_VERITY")
DEFAULT_FILE_STORAGE = os.environ.get("DEFAULT_FILE_STORAGE")
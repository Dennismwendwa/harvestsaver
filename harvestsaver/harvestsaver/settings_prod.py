from .settings import *

DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY")
YOUR_DOMAIN = "https://pysoftware.tech"

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
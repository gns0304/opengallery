from os import getenv

def as_bool(val, default=False):
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "t", "yes", "y", "on"}

# Debug Environment
PRODUCTION = as_bool(getenv('PRODUCTION', False))

ALLOWED_HOSTS = getenv('ALLOWED_HOSTS', '*').split(',')

# Secret Environment
SECRET_KEY = getenv('SECRET_KEY', 'django-insecure-f@3r(9xb@$&*33c0@-x&pl5!6&a@+!(1nsjiohc^$dkdaxy$ai')

# Database Config
USE_CUSTOM_DB = as_bool(getenv("USE_CUSTOM_DB", False))
CUSTOM_DB_ENGINE = getenv(
    "CUSTOM_DB_ENGINE", "django.db.backends.postgresql")
CUSTOM_DB_NAME = getenv("PGDATABASE")
CUSTOM_DB_USER = getenv("PGUSER")
CUSTOM_DB_PASSWORD = getenv("PGPASSWORD")
CUSTOM_DB_HOST = getenv("PGHOST")
CUSTOM_DB_PORT = getenv("PGPORT")

# Media Config

USE_S3_MEDIA = as_bool(getenv("USE_S3_MEDIA", False))
AWS_S3_ACCESS_KEY_ID = getenv("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = getenv("AWS_S3_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = getenv("AWS_S3_REGION_NAME", "ap-northeast-2")
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_ADDRESSING_STYLE  = "virtual"
AWS_STORAGE_BUCKET_NAME = getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = getenv("AWS_S3_CUSTOM_DOMAIN", f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com")
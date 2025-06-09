from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class PublicMediaStorage(S3Boto3Storage):
    location = f'{settings.S3_ENV}/media'
    file_overwrite = False

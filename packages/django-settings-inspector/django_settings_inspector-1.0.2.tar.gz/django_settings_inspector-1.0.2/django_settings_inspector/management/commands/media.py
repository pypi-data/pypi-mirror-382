#!/usr/bin/env python3
# file: commands/media.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django MEDIA-related settings with colored output
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    help = "Show Django MEDIA-related settings"

    def handle(self, *args, **options):
        data = {
            # Django core
            "MEDIA_URL": getattr(settings, "MEDIA_URL", None),
            "MEDIA_ROOT": getattr(settings, "MEDIA_ROOT", None),

            # Custom / storage backend settings (optional)
            "DEFAULT_FILE_STORAGE": getattr(settings, "DEFAULT_FILE_STORAGE", None),
            "FILE_UPLOAD_HANDLERS": getattr(settings, "FILE_UPLOAD_HANDLERS", None),
            "FILE_UPLOAD_MAX_MEMORY_SIZE": getattr(settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", None),
            "FILE_UPLOAD_PERMISSIONS": getattr(settings, "FILE_UPLOAD_PERMISSIONS", None),
            "FILE_UPLOAD_DIRECTORY_PERMISSIONS": getattr(settings, "FILE_UPLOAD_DIRECTORY_PERMISSIONS", None),
            "FILE_UPLOAD_TEMP_DIR": getattr(settings, "FILE_UPLOAD_TEMP_DIR", None),
            "MEDIA_STORAGE_BACKEND": getattr(settings, "MEDIA_STORAGE_BACKEND", None),

            # Remote storages (opsional / third party)
            "AWS_STORAGE_BUCKET_NAME": getattr(settings, "AWS_STORAGE_BUCKET_NAME", None),
            "AWS_S3_REGION_NAME": getattr(settings, "AWS_S3_REGION_NAME", None),
            "AWS_S3_CUSTOM_DOMAIN": getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None),
            "AZURE_ACCOUNT_NAME": getattr(settings, "AZURE_ACCOUNT_NAME", None),
            "AZURE_CONTAINER": getattr(settings, "AZURE_CONTAINER", None),
            "CLOUDINARY_URL": getattr(settings, "CLOUDINARY_URL", None),
        }

        self.render_data(data, options)
#!/usr/bin/env python3
# file: commands/storage.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django file and storage-related settings
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    """Django management command To display storage-related settings"""

    help = "Show Django storage and file upload settings"

    def handle(self, *args, **options):
        data = {
            "DEFAULT_FILE_STORAGE": getattr(settings, "DEFAULT_FILE_STORAGE", None),
            "STORAGES": getattr(settings, "STORAGES", None),
            "MEDIA_ROOT": getattr(settings, "MEDIA_ROOT", None),
            "MEDIA_URL": getattr(settings, "MEDIA_URL", None),
            "FILE_UPLOAD_HANDLERS": getattr(settings, "FILE_UPLOAD_HANDLERS", None),
            "FILE_UPLOAD_MAX_MEMORY_SIZE": getattr(settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", None),
            "FILE_UPLOAD_PERMISSIONS": getattr(settings, "FILE_UPLOAD_PERMISSIONS", None),
            "FILE_UPLOAD_DIRECTORY_PERMISSIONS": getattr(settings, "FILE_UPLOAD_DIRECTORY_PERMISSIONS", None),
            "DATA_UPLOAD_MAX_MEMORY_SIZE": getattr(settings, "DATA_UPLOAD_MAX_MEMORY_SIZE", None),
            "DATA_UPLOAD_MAX_NUMBER_FIELDS": getattr(settings, "DATA_UPLOAD_MAX_NUMBER_FIELDS", None),
            "FILE_CHARSET": getattr(settings, "FILE_CHARSET", None),
        }

        self.render_data(data, options)
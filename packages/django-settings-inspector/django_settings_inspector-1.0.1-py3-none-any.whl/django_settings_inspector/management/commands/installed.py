#!/usr/bin/env python3
# file: commands/installed.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django INSTALLED_APPS and related settings with colored output
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    help = "Show Django INSTALLED_APPS and related settings"

    def handle(self, *args, **options):
        # Semua setting yang berhubungan dengan aplikasi
        data = {
            "INSTALLED_APPS": getattr(settings, "INSTALLED_APPS", None),
            "DEFAULT_AUTO_FIELD": getattr(settings, "DEFAULT_AUTO_FIELD", None),
            "MIGRATION_MODULES": getattr(settings, "MIGRATION_MODULES", None),
            "APPEND_SLASH": getattr(settings, "APPEND_SLASH", None),
            "ROOT_URLCONF": getattr(settings, "ROOT_URLCONF", None),
            "WSGI_APPLICATION": getattr(settings, "WSGI_APPLICATION", None),
            "ASGI_APPLICATION": getattr(settings, "ASGI_APPLICATION", None),
            "ADMIN_SITE_HEADER": getattr(settings, "ADMIN_SITE_HEADER", None),
            "ADMIN_SITE_TITLE": getattr(settings, "ADMIN_SITE_TITLE", None),
            "ADMIN_INDEX_TITLE": getattr(settings, "ADMIN_INDEX_TITLE", None),
        }

        self.render_data(data, options)
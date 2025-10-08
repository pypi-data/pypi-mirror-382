#!/usr/bin/env python3
# file: commands/site.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django site-level and environment settings
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    """Django management command to display sites and environment settings"""

    help = "Show Django site and environment-level settings"

    def handle(self, *args, **options):
        data = {
            "BASE_DIR": getattr(settings, "BASE_DIR", None),
            "ROOT_URLCONF": getattr(settings, "ROOT_URLCONF", None),
            "WSGI_APPLICATION": getattr(settings, "WSGI_APPLICATION", None),
            "ASGI_APPLICATION": getattr(settings, "ASGI_APPLICATION", None),
            "ALLOWED_HOSTS": getattr(settings, "ALLOWED_HOSTS", None),
            "LANGUAGE_CODE": getattr(settings, "LANGUAGE_CODE", None),
            "TIME_ZONE": getattr(settings, "TIME_ZONE", None),
            "USE_I18N": getattr(settings, "USE_I18N", None),
            "USE_L10N": getattr(settings, "USE_L10N", None) if hasattr(settings, "USE_L10N") else None,
            "USE_TZ": getattr(settings, "USE_TZ", None),
            "DEBUG": getattr(settings, "DEBUG", None),
            "SECRET_KEY": getattr(settings, "SECRET_KEY", None),
            "DEFAULT_AUTO_FIELD": getattr(settings, "DEFAULT_AUTO_FIELD", None),
            "SITE_ID": getattr(settings, "SITE_ID", None),
        }

        self.render_data(data, options)
#!/usr/bin/env python3
# file: commands/session.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django session-related settings
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    
    help = "Show Django session-related settings"

    def handle(self, *args, **options):
        data = {
            "SESSION_ENGINE": getattr(settings, "SESSION_ENGINE", None),
            "SESSION_COOKIE_NAME": getattr(settings, "SESSION_COOKIE_NAME", None),
            "SESSION_COOKIE_AGE": getattr(settings, "SESSION_COOKIE_AGE", None),
            "SESSION_COOKIE_DOMAIN": getattr(settings, "SESSION_COOKIE_DOMAIN", None),
            "SESSION_COOKIE_PATH": getattr(settings, "SESSION_COOKIE_PATH", None),
            "SESSION_COOKIE_SECURE": getattr(settings, "SESSION_COOKIE_SECURE", None),
            "SESSION_COOKIE_HTTPONLY": getattr(settings, "SESSION_COOKIE_HTTPONLY", None),
            "SESSION_EXPIRE_AT_BROWSER_CLOSE": getattr(settings, "SESSION_EXPIRE_AT_BROWSER_CLOSE", None),
            "SESSION_SAVE_EVERY_REQUEST": getattr(settings, "SESSION_SAVE_EVERY_REQUEST", None),
            "SESSION_SERIALIZER": getattr(settings, "SESSION_SERIALIZER", None),
            "SESSION_FILE_PATH": getattr(settings, "SESSION_FILE_PATH", None),
            "SESSION_CACHE_ALIAS": getattr(settings, "SESSION_CACHE_ALIAS", None),
        }

        self.render_data(data, options)
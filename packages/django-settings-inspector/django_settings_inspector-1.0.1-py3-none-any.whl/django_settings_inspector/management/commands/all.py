#!/usr/bin/env python3
# file: commands/all.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show all main Django settings (with optional keyword filter)
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    """Django management command to display all main settings (with an optional filter)"""

    help = "Show all Django settings grouped by category. Use --filter <keyword> to narrow results."

    def handle(self, *args, **options):
        keyword = options.get('filter')
        keyword_lower = keyword.lower() if keyword else None

        categories = {
            "DATABASES": getattr(settings, "DATABASES", None),
            "CACHES": getattr(settings, "CACHES", None),
            "INSTALLED_APPS": getattr(settings, "INSTALLED_APPS", None),
            "MIDDLEWARE": getattr(settings, "MIDDLEWARE", None),
            "TEMPLATES": getattr(settings, "TEMPLATES", None),
            "EMAIL": {
                "EMAIL_BACKEND": getattr(settings, "EMAIL_BACKEND", None),
                "EMAIL_HOST": getattr(settings, "EMAIL_HOST", None),
                "EMAIL_PORT": getattr(settings, "EMAIL_PORT", None),
                "DEFAULT_FROM_EMAIL": getattr(settings, "DEFAULT_FROM_EMAIL", None),
            },
            "STATIC": {
                "STATIC_URL": getattr(settings, "STATIC_URL", None),
                "STATICFILES_DIRS": getattr(settings, "STATICFILES_DIRS", None),
                "STATIC_ROOT": getattr(settings, "STATIC_ROOT", None),
            },
            "MEDIA": {
                "MEDIA_URL": getattr(settings, "MEDIA_URL", None),
                "MEDIA_ROOT": getattr(settings, "MEDIA_ROOT", None),
            },
            "AUTH": {
                "AUTH_USER_MODEL": getattr(settings, "AUTH_USER_MODEL", None),
                "LOGIN_URL": getattr(settings, "LOGIN_URL", None),
                "LOGIN_REDIRECT_URL": getattr(settings, "LOGIN_REDIRECT_URL", None),
            },
            "SECURITY": {
                "CSRF_COOKIE_SECURE": getattr(settings, "CSRF_COOKIE_SECURE", None),
                "SECURE_SSL_REDIRECT": getattr(settings, "SECURE_SSL_REDIRECT", None),
                "SESSION_COOKIE_SECURE": getattr(settings, "SESSION_COOKIE_SECURE", None),
            },
        }

        self.render_data(categories, options)
#!/usr/bin/env python3
# file: commands/security.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django security & HTTPS-related settings
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    help = "Show Django security and HTTPS-related settings"

    def handle(self, *args, **options):
        data = {
            "CSRF_COOKIE_SECURE": getattr(settings, "CSRF_COOKIE_SECURE", None),
            "CSRF_TRUSTED_ORIGINS": getattr(settings, "CSRF_TRUSTED_ORIGINS", None),
            "SECURE_SSL_REDIRECT": getattr(settings, "SECURE_SSL_REDIRECT", None),
            "SECURE_HSTS_SECONDS": getattr(settings, "SECURE_HSTS_SECONDS", None),
            "SECURE_HSTS_INCLUDE_SUBDOMAINS": getattr(settings, "SECURE_HSTS_INCLUDE_SUBDOMAINS", None),
            "SECURE_HSTS_PRELOAD": getattr(settings, "SECURE_HSTS_PRELOAD", None),
            "SECURE_REFERRER_POLICY": getattr(settings, "SECURE_REFERRER_POLICY", None),
            "SESSION_COOKIE_SECURE": getattr(settings, "SESSION_COOKIE_SECURE", None),
            "SESSION_COOKIE_HTTPONLY": getattr(settings, "SESSION_COOKIE_HTTPONLY", None),
            "SESSION_EXPIRE_AT_BROWSER_CLOSE": getattr(settings, "SESSION_EXPIRE_AT_BROWSER_CLOSE", None),
            "X_FRAME_OPTIONS": getattr(settings, "X_FRAME_OPTIONS", None),
            "CSRF_COOKIE_HTTPONLY": getattr(settings, "CSRF_COOKIE_HTTPONLY", None),
            "SECURE_PROXY_SSL_HEADER": getattr(settings, "SECURE_PROXY_SSL_HEADER", None),
        }

        self.render_data(data, options)
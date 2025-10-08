#!/usr/bin/env python3
# file: commands/auth.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django authentication and user-related settings
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):

    help = "Show Django authentication and user-related settings"

    def handle(self, *args, **options):
        data = {
            "AUTH_USER_MODEL": getattr(settings, "AUTH_USER_MODEL", None),
            "AUTHENTICATION_BACKENDS": getattr(settings, "AUTHENTICATION_BACKENDS", None),
            "LOGIN_URL": getattr(settings, "LOGIN_URL", None),
            "LOGIN_REDIRECT_URL": getattr(settings, "LOGIN_REDIRECT_URL", None),
            "LOGOUT_REDIRECT_URL": getattr(settings, "LOGOUT_REDIRECT_URL", None),
            "PASSWORD_HASHERS": getattr(settings, "PASSWORD_HASHERS", None),
            "PASSWORD_RESET_TIMEOUT": getattr(settings, "PASSWORD_RESET_TIMEOUT", None),
            "PASSWORD_RESET_TIMEOUT_DAYS": getattr(settings, "PASSWORD_RESET_TIMEOUT_DAYS", None),
            "SESSION_COOKIE_AGE": getattr(settings, "SESSION_COOKIE_AGE", None),
            "SESSION_ENGINE": getattr(settings, "SESSION_ENGINE", None),
            "SESSION_COOKIE_NAME": getattr(settings, "SESSION_COOKIE_NAME", None),
            "SESSION_SAVE_EVERY_REQUEST": getattr(settings, "SESSION_SAVE_EVERY_REQUEST", None),
            "SESSION_EXPIRE_AT_BROWSER_CLOSE": getattr(settings, "SESSION_EXPIRE_AT_BROWSER_CLOSE", None),
            "SESSION_COOKIE_SECURE": getattr(settings, "SESSION_COOKIE_SECURE", None),
            "SESSION_COOKIE_HTTPONLY": getattr(settings, "SESSION_COOKIE_HTTPONLY", None),
        }

        self.render_data(data, options)
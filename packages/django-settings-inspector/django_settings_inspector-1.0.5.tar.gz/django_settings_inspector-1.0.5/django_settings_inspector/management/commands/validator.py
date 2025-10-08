#!/usr/bin/env python3
# file: commands/validator.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django *VALIDATORS settings with colored output
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    """
    Show Django *VALIDATORS and related password/auth settings with colored output
    """

    help = "Show Django *VALIDATORS settings"

    def handle(self, *args, **options):
        data = {
            # Password validation
            "AUTH_PASSWORD_VALIDATORS": getattr(settings, "AUTH_PASSWORD_VALIDATORS", None),

            # Hashing and password-related
            "PASSWORD_HASHERS": getattr(settings, "PASSWORD_HASHERS", None),
            "PASSWORD_RESET_TIMEOUT": getattr(settings, "PASSWORD_RESET_TIMEOUT", None),
            "PASSWORD_RESET_TIMEOUT_DAYS": getattr(settings, "PASSWORD_RESET_TIMEOUT_DAYS", None),  # legacy

            # Other possible validators (custom)
            "USER_VALIDATORS": getattr(settings, "USER_VALIDATORS", None),
            "EMAIL_VALIDATORS": getattr(settings, "EMAIL_VALIDATORS", None),
            "USERNAME_VALIDATORS": getattr(settings, "USERNAME_VALIDATORS", None),

            # Auth system related
            "AUTH_USER_MODEL": getattr(settings, "AUTH_USER_MODEL", None),
            "AUTHENTICATION_BACKENDS": getattr(settings, "AUTHENTICATION_BACKENDS", None),
            "LOGIN_URL": getattr(settings, "LOGIN_URL", None),
            "LOGIN_REDIRECT_URL": getattr(settings, "LOGIN_REDIRECT_URL", None),
            "LOGOUT_REDIRECT_URL": getattr(settings, "LOGOUT_REDIRECT_URL", None),
        }

        self.render_data(data, options)
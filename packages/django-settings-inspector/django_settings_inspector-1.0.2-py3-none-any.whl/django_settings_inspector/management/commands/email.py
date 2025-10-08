#!/usr/bin/env python3
# file: commands/email.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django email-related settings
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    """
    Django management command To display configuration EMAIL
    """

    help = "Show Django email-related settings"

    def handle(self, *args, **options):
        data = {
            "EMAIL_BACKEND": getattr(settings, "EMAIL_BACKEND", None),
            "EMAIL_HOST": getattr(settings, "EMAIL_HOST", None),
            "EMAIL_PORT": getattr(settings, "EMAIL_PORT", None),
            "EMAIL_HOST_USER": getattr(settings, "EMAIL_HOST_USER", None),
            "EMAIL_HOST_PASSWORD": getattr(settings, "EMAIL_HOST_PASSWORD", None),
            "EMAIL_USE_TLS": getattr(settings, "EMAIL_USE_TLS", None),
            "EMAIL_USE_SSL": getattr(settings, "EMAIL_USE_SSL", None),
            "EMAIL_TIMEOUT": getattr(settings, "EMAIL_TIMEOUT", None),
            "EMAIL_SSL_CERTFILE": getattr(settings, "EMAIL_SSL_CERTFILE", None),
            "EMAIL_SSL_KEYFILE": getattr(settings, "EMAIL_SSL_KEYFILE", None),
            "EMAIL_FROM": getattr(settings, "EMAIL_FROM", None),
            "DEFAULT_FROM_EMAIL": getattr(settings, "DEFAULT_FROM_EMAIL", None),
            "SERVER_EMAIL": getattr(settings, "SERVER_EMAIL", None),
            "ADMINS": getattr(settings, "ADMINS", None),
            "MANAGERS": getattr(settings, "MANAGERS", None),
        }

        self.render_data(data, options)
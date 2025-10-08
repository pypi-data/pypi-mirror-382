#!/usr/bin/env python3
# file: commands/static.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django static file settings with colored output
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    help = "Show Django static file settings"

    def handle(self, *args, **options):
        data = {
            "STATIC_URL": getattr(settings, "STATIC_URL", None),
            "STATIC_ROOT": getattr(settings, "STATIC_ROOT", None),
            "STATICFILES_DIRS": getattr(settings, "STATICFILES_DIRS", None),
            "STATICFILES_FINDERS": getattr(settings, "STATICFILES_FINDERS", None),
            "STATICFILES_STORAGE": getattr(settings, "STATICFILES_STORAGE", None),
            "WHITENOISE_AUTOREFRESH": getattr(settings, "WHITENOISE_AUTOREFRESH", None),
            "WHITENOISE_USE_FINDERS": getattr(settings, "WHITENOISE_USE_FINDERS", None),
            "WHITENOISE_MANIFEST_STRICT": getattr(settings, "WHITENOISE_MANIFEST_STRICT", None),
            "WHITENOISE_ROOT": getattr(settings, "WHITENOISE_ROOT", None),
        }

        self.render_data(data, options)
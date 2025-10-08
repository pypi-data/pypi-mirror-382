#!/usr/bin/env python3
# file: commands/locale.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django locale settings (LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_TZ)
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    """Show Django locale (language & timezone) settings."""

    help = "Show Django locale (language & timezone) settings."

    def handle(self, *args, **options):
        data = {
            "LANGUAGE_CODE": getattr(settings, "LANGUAGE_CODE", None),
            "TIME_ZONE": getattr(settings, "TIME_ZONE", None),
            "USE_I18N": getattr(settings, "USE_I18N", None),
            "USE_TZ": getattr(settings, "USE_TZ", None),
        }

        self.render_data(data, options)
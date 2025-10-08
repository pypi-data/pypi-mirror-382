#!/usr/bin/env python3
# file: commands/core.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django CORE settings (BASE_DIR, DEBUG, SECRET_KEY, ALLOWED_HOSTS)
# License: MIT

import os
from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    help = "Show core environment settings"

    def handle(self, *args, **options):
        data = {
            "BASE_DIR": getattr(settings, "BASE_DIR", None),
            "DEBUG": getattr(settings, "DEBUG", None),
            "SECRET_KEY": getattr(settings, "SECRET_KEY", None),
            "ALLOWED_HOSTS": getattr(settings, "ALLOWED_HOSTS", None),
        }
        # Masking is handled by base
        self.render_data(data, options)

#!/usr/bin/env python3
# file: commands/db.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django database-related settings (DATABASES, DEFAULT_AUTO_FIELD)
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    help = "Show database-related settings"

    def handle(self, *args, **options):
        data = {
            "DATABASES": getattr(settings, "DATABASES", None),
            "DEFAULT_AUTO_FIELD": getattr(settings, "DEFAULT_AUTO_FIELD", None),
        }
        self.render_data(data, options)

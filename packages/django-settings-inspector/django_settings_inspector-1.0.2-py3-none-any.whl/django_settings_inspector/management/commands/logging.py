#!/usr/bin/env python3
# file: commands/logging.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django LOGGING-related settings with colored output
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    """
    Show Django LOGGING configuration and related variables
    """

    help = "Show Django LOGGING-related settings"

    def handle(self, *args, **options):
        data = {
            "LOGGING": getattr(settings, "LOGGING", None),
            "LOGGING_CONFIG": getattr(settings, "LOGGING_CONFIG", None),
            "DEFAULT_LOGGING": getattr(settings, "DEFAULT_LOGGING", None),
            "SERVER_LOGGER": getattr(settings, "SERVER_LOGGER", None),
            "CONSOLE_LOGGER": getattr(settings, "CONSOLE_LOGGER", None),
            "FILE_LOGGER": getattr(settings, "FILE_LOGGER", None),
            "REQUEST_LOGGING": getattr(settings, "REQUEST_LOGGING", None),
            "SILENCED_SYSTEM_CHECKS": getattr(settings, "SILENCED_SYSTEM_CHECKS", None),
            "DEBUG_PROPAGATE_EXCEPTIONS": getattr(settings, "DEBUG_PROPAGATE_EXCEPTIONS", None),
        }

        self.render_data(data, options)
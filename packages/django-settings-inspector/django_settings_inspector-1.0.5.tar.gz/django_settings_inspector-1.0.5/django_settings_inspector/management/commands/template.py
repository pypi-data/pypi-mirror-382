#!/usr/bin/env python3
# file: commands/template.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django template-related settings with colored output
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    """
    Show Django TEMPLATES and related settings with colored output
    """

    def _get_template_option(self, key):
        try:
            templates = getattr(settings, "TEMPLATES", None)
            if templates and isinstance(templates, (list, tuple)) and "OPTIONS" in templates[0]:
                return templates[0]["OPTIONS"].get(key)
        except Exception:
            pass
        return None

    def handle(self, *args, **options):
        data = {
            # Django 1.8+ unified system
            "TEMPLATES": getattr(settings, "TEMPLATES", None),

            # Legacy (Django <1.8) — masih muncul kadang di proyek lama
            "TEMPLATE_DIRS": getattr(settings, "TEMPLATE_DIRS", None),
            "TEMPLATE_LOADERS": getattr(settings, "TEMPLATE_LOADERS", None),
            "TEMPLATE_CONTEXT_PROCESSORS": getattr(settings, "TEMPLATE_CONTEXT_PROCESSORS", None),
            "TEMPLATE_DEBUG": getattr(settings, "TEMPLATE_DEBUG", None),

            # Related general flags
            "DEBUG": getattr(settings, "DEBUG", None),
            "ALLOWED_HOSTS": getattr(settings, "ALLOWED_HOSTS", None),
            "INSTALLED_APPS": getattr(settings, "INSTALLED_APPS", None),

            # Custom Jinja2 support (opsional)
            "JINJA2_ENVIRONMENT_OPTIONS": getattr(settings, "JINJA2_ENVIRONMENT_OPTIONS", None),
            "JINJA2_TEMPLATE_LOADERS": getattr(settings, "JINJA2_TEMPLATE_LOADERS", None),

            # Cached template loader info (untuk debug)
            "OPTIONS_DEBUG_TEMPLATES": self._get_template_option("debug"),
            "OPTIONS_LOADERS": self._get_template_option("loaders"),
            "OPTIONS_CONTEXT_PROCESSORS": self._get_template_option("context_processors"),
        }

        self.render_data(data, options)
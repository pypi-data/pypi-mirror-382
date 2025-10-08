#!/usr/bin/env python3
# file: commands/cache.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django cache-related settings with colored output
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    help = "Show Django cache-related settings"

    def handle(self, *args, **options):
        data = {
            # Core cache configuration
            "CACHES": getattr(settings, "CACHES", None),
            "CACHE_MIDDLEWARE_ALIAS": getattr(settings, "CACHE_MIDDLEWARE_ALIAS", None),
            "CACHE_MIDDLEWARE_KEY_PREFIX": getattr(settings, "CACHE_MIDDLEWARE_KEY_PREFIX", None),
            "CACHE_MIDDLEWARE_SECONDS": getattr(settings, "CACHE_MIDDLEWARE_SECONDS", None),

            # Per-cache backend opsional (umum digunakan)
            "DEFAULT_CACHE_ALIAS": getattr(settings, "DEFAULT_CACHE_ALIAS", None),

            # Session cache backend
            "SESSION_ENGINE": getattr(settings, "SESSION_ENGINE", None),
            "SESSION_CACHE_ALIAS": getattr(settings, "SESSION_CACHE_ALIAS", None),

            # Template caching
            "TEMPLATES": getattr(settings, "TEMPLATES", None),

            # Middleware flags
            "USE_ETAGS": getattr(settings, "USE_ETAGS", None),
            "CONDITIONAL_GET_MIDDLEWARE": "django.middleware.http.ConditionalGetMiddleware" in getattr(settings, "MIDDLEWARE", []),
            "GZIP_MIDDLEWARE": "django.middleware.gzip.GZipMiddleware" in getattr(settings, "MIDDLEWARE", []),

            # Security & common interactions
            "SECURE_BROWSER_XSS_FILTER": getattr(settings, "SECURE_BROWSER_XSS_FILTER", None),
            "SECURE_CONTENT_TYPE_NOSNIFF": getattr(settings, "SECURE_CONTENT_TYPE_NOSNIFF", None),

            # Custom cache settings (jika digunakan dengan library pihak ketiga)
            "CACHEOPS_REDIS": getattr(settings, "CACHEOPS_REDIS", None),
            "CACHEOPS": getattr(settings, "CACHEOPS", None),
            "CACHEOPS_DEFAULTS": getattr(settings, "CACHEOPS_DEFAULTS", None),

            # Django Debug Toolbar cache panels
            "DEBUG_TOOLBAR_PANELS": getattr(settings, "DEBUG_TOOLBAR_PANELS", None),
        }

        self.render_data(data, options)
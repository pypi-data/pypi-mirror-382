#!/usr/bin/env python3
# file: commands/middleware.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-07
# Description: Show Django MIDDLEWARE-related settings with colored output
# License: MIT

from django.conf import settings
from django_settings_inspector.base import BaseInspectorCommand

class Command(BaseInspectorCommand):
    help = "Show Django MIDDLEWARE-related settings"

    def handle(self, *args, **options):
        data = {
            # Core middleware
            "MIDDLEWARE": getattr(settings, "MIDDLEWARE", None),
            "MIDDLEWARE_CLASSES": getattr(settings, "MIDDLEWARE_CLASSES", None),  # legacy

            # Security-related
            "SECURE_BROWSER_XSS_FILTER": getattr(settings, "SECURE_BROWSER_XSS_FILTER", None),
            "SECURE_CONTENT_TYPE_NOSNIFF": getattr(settings, "SECURE_CONTENT_TYPE_NOSNIFF", None),
            "SECURE_HSTS_INCLUDE_SUBDOMAINS": getattr(settings, "SECURE_HSTS_INCLUDE_SUBDOMAINS", None),
            "SECURE_HSTS_PRELOAD": getattr(settings, "SECURE_HSTS_PRELOAD", None),
            "SECURE_HSTS_SECONDS": getattr(settings, "SECURE_HSTS_SECONDS", None),
            "SECURE_PROXY_SSL_HEADER": getattr(settings, "SECURE_PROXY_SSL_HEADER", None),
            "SECURE_REFERRER_POLICY": getattr(settings, "SECURE_REFERRER_POLICY", None),
            "SECURE_SSL_REDIRECT": getattr(settings, "SECURE_SSL_REDIRECT", None),

            # CSRF middleware-related
            "CSRF_COOKIE_HTTPONLY": getattr(settings, "CSRF_COOKIE_HTTPONLY", None),
            "CSRF_COOKIE_NAME": getattr(settings, "CSRF_COOKIE_NAME", None),
            "CSRF_COOKIE_PATH": getattr(settings, "CSRF_COOKIE_PATH", None),
            "CSRF_COOKIE_SAMESITE": getattr(settings, "CSRF_COOKIE_SAMESITE", None),
            "CSRF_COOKIE_SECURE": getattr(settings, "CSRF_COOKIE_SECURE", None),
            "CSRF_FAILURE_VIEW": getattr(settings, "CSRF_FAILURE_VIEW", None),
            "CSRF_HEADER_NAME": getattr(settings, "CSRF_HEADER_NAME", None),
            "CSRF_TRUSTED_ORIGINS": getattr(settings, "CSRF_TRUSTED_ORIGINS", None),
            "CSRF_USE_SESSIONS": getattr(settings, "CSRF_USE_SESSIONS", None),

            # Session middleware-related
            "SESSION_COOKIE_AGE": getattr(settings, "SESSION_COOKIE_AGE", None),
            "SESSION_COOKIE_DOMAIN": getattr(settings, "SESSION_COOKIE_DOMAIN", None),
            "SESSION_COOKIE_HTTPONLY": getattr(settings, "SESSION_COOKIE_HTTPONLY", None),
            "SESSION_COOKIE_NAME": getattr(settings, "SESSION_COOKIE_NAME", None),
            "SESSION_COOKIE_PATH": getattr(settings, "SESSION_COOKIE_PATH", None),
            "SESSION_COOKIE_SAMESITE": getattr(settings, "SESSION_COOKIE_SAMESITE", None),
            "SESSION_COOKIE_SECURE": getattr(settings, "SESSION_COOKIE_SECURE", None),
            "SESSION_ENGINE": getattr(settings, "SESSION_ENGINE", None),
            "SESSION_EXPIRE_AT_BROWSER_CLOSE": getattr(settings, "SESSION_EXPIRE_AT_BROWSER_CLOSE", None),
            "SESSION_FILE_PATH": getattr(settings, "SESSION_FILE_PATH", None),
            "SESSION_SAVE_EVERY_REQUEST": getattr(settings, "SESSION_SAVE_EVERY_REQUEST", None),
            "SESSION_SERIALIZER": getattr(settings, "SESSION_SERIALIZER", None),

            # GZip / Cache / Conditional GET middleware
            "GZIP_MIDDLEWARE": "django.middleware.gzip.GZipMiddleware" in getattr(settings, "MIDDLEWARE", []),
            "CONDITIONAL_GET_MIDDLEWARE": "django.middleware.http.ConditionalGetMiddleware" in getattr(settings, "MIDDLEWARE", []),
            "CACHE_MIDDLEWARE_ALIAS": getattr(settings, "CACHE_MIDDLEWARE_ALIAS", None),
            "CACHE_MIDDLEWARE_SECONDS": getattr(settings, "CACHE_MIDDLEWARE_SECONDS", None),
            "CACHE_MIDDLEWARE_KEY_PREFIX": getattr(settings, "CACHE_MIDDLEWARE_KEY_PREFIX", None),

            # Clickjacking
            "X_FRAME_OPTIONS": getattr(settings, "X_FRAME_OPTIONS", None),

            # Common & Localization
            "USE_X_FORWARDED_HOST": getattr(settings, "USE_X_FORWARDED_HOST", None),
            "USE_X_FORWARDED_PORT": getattr(settings, "USE_X_FORWARDED_PORT", None),
            "LANGUAGE_COOKIE_NAME": getattr(settings, "LANGUAGE_COOKIE_NAME", None),
            "LANGUAGE_COOKIE_SECURE": getattr(settings, "LANGUAGE_COOKIE_SECURE", None),
            "LANGUAGE_COOKIE_HTTPONLY": getattr(settings, "LANGUAGE_COOKIE_HTTPONLY", None),

            # CORS (is use django-cors-headers)
            "CORS_ALLOWED_ORIGINS": getattr(settings, "CORS_ALLOWED_ORIGINS", None),
            "CORS_ALLOW_ALL_ORIGINS": getattr(settings, "CORS_ALLOW_ALL_ORIGINS", None),
            "CORS_ALLOW_CREDENTIALS": getattr(settings, "CORS_ALLOW_CREDENTIALS", None),
            "CORS_ALLOW_HEADERS": getattr(settings, "CORS_ALLOW_HEADERS", None),
            "CORS_EXPOSE_HEADERS": getattr(settings, "CORS_EXPOSE_HEADERS", None),
            "CORS_PREFLIGHT_MAX_AGE": getattr(settings, "CORS_PREFLIGHT_MAX_AGE", None),
        }

        self.render_data(data, options)
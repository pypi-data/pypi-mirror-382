"""
Integration tests for django-settings-inspector modular settings.
"""

import importlib


def test_all_contains_core_settings():
    mod = importlib.import_module("django_settings_inspector.management.commands.all")
    for key in ["INSTALLED_APPS", "DATABASES", "LANGUAGE_CODE"]:
        assert hasattr(mod, key), f"Missing {key} in {mod.__name__}"


def test_security_settings_exist():
    mod = importlib.import_module("django_settings_inspector.management.commands.security")
    expected = ["SECURE_SSL_REDIRECT", "SESSION_COOKIE_SECURE", "CSRF_COOKIE_SECURE"]
    for key in expected:
        assert hasattr(mod, key)

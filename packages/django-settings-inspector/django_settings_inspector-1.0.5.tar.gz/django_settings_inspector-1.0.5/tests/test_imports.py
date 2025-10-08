"""
Ensure all modules in django_settings_inspector are importable.
"""

import importlib
import pytest

modules = [
    "django_settings_inspector.management.commands.all",
    "django_settings_inspector.management.commands.core",
    "django_settings_inspector.management.commands.db",
    "django_settings_inspector.management.commands.auth",
    "django_settings_inspector.management.commands.cache",
    "django_settings_inspector.management.commands.security",
    "django_settings_inspector.management.commands.locale",
    "django_settings_inspector.management.commands.static",
    "django_settings_inspector.management.commands.site",
    "django_settings_inspector.management.commands.template",
    "django_settings_inspector.management.commands.validator",
]


@pytest.mark.parametrize("mod", modules)
def test_imports_ok(mod):
    module = importlib.import_module(mod)
    assert hasattr(module, "Command"), f"{mod} missing Command class"

"""
Global pytest configuration for django-settings-inspector.
Provides a fake Django environment and mocks django-admin if not installed.
"""

import sys
import types
import pytest


@pytest.fixture(scope="session", autouse=True)
def mock_django_env(monkeypatch):
    """
    Create a minimal fake Django environment so the package
    can be imported even if Django is not installed.
    """
    fake_django = types.ModuleType("django")
    fake_conf = types.ModuleType("django.conf")
    fake_conf.settings = types.SimpleNamespace(
        DEBUG=True,
        SECRET_KEY="fake-secret-key",
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        INSTALLED_APPS=["django.contrib.admin"],
        STATIC_URL="/static/",
        LANGUAGE_CODE="en-us",
        TIME_ZONE="UTC",
    )

    # Mock django.core.management.commands.diffsettings
    fake_mgmt = types.ModuleType("django.core.management.commands")
    fake_diffsettings = types.ModuleType("django.core.management.commands.diffsettings")

    class BaseCommand:
        """Dummy base class simulating Django management Command"""
        def __init__(self):
            self.stdout = sys.stdout

        def handle(self, *args, **kwargs):
            pass

    fake_diffsettings.Command = BaseCommand

    fake_django.conf = fake_conf
    fake_django.core = types.ModuleType("django.core")
    fake_django.core.management = types.ModuleType("django.core.management")
    fake_django.core.management.commands = fake_mgmt
    fake_mgmt.diffsettings = fake_diffsettings

    sys.modules["django"] = fake_django
    sys.modules["django.conf"] = fake_conf
    sys.modules["django.core"] = fake_django.core
    sys.modules["django.core.management"] = fake_django.core.management
    sys.modules["django.core.management.commands"] = fake_mgmt
    sys.modules["django.core.management.commands.diffsettings"] = fake_diffsettings

    yield  # return control to test

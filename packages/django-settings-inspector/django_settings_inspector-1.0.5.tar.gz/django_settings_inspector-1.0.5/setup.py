from setuptools import setup, find_packages
import os
from pathlib import Path
import traceback
import shutil

NAME = "django_settings_inspector"
this_directory = os.path.abspath(os.path.dirname(__file__))

if (Path(__file__).parent / '__version__.py').is_file():
    shutil.copy(str((Path(__file__).parent / '__version__.py')), os.path.join(this_directory, NAME, '__version__.py'))

def get_version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if not version_file.is_file():
            version_file = Path(__file__).parent / NAME / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK', "0").lower() in ['1', 'true', 'yes']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "0.1.0"

print(f"VERSION: {get_version()}")

setup(
    name=NAME,
    version=get_version(),
    author="Hadi Cahyadi",
    author_email="cumulus13@gmail.com",
    description="A Django management and CLI tool to inspect and colorize project settings",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cumulus13/django-settings-inspector",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "Django>=3.2",
        "rich>=13.0",
    ],
    entry_points={
        "console_scripts": [
            "djinspect=django_settings_inspector.cli:main",
        ],
    },
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
)

from pathlib import Path
import os
import traceback

os.environ.update({"TRACEBACK":"1"})

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

__version__ = get_version()
__author__ = "Hadi Cahyadi <cumulus13@gmail.com>"

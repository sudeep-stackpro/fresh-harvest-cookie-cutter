#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def main():
    """Run administrative tasks."""
    env_path = Path(__file__).resolve().parent / ".envs" / ".local" / ".django"
    load_dotenv(dotenv_path=env_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

    try:
        from django.core.management import execute_from_command_line  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(  # noqa: TRY003
            "Couldn't import Django. Are you sure it's installed and "  # noqa: EM101
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?",
        ) from exc

    # This allows easy placement of apps within the interior
    # fresh_harvest directory.
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path / "fresh_harvest"))

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

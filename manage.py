#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "API.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Configure logger
    logger = logging.getLogger('django')

    try:
        from django.core.management import execute_from_command_line

        # Log ici pour vérifier le mode DEBUG
        from django.conf import settings
        logger.info(f'DEBUG mode is set to {settings.DEBUG}')
        print(f'DEBUG mode is set to {settings.DEBUG}')  # Vérification supplémentaire

        execute_from_command_line(sys.argv)
    except Exception as e:
        logger.error('An error occurred: %s', e)
        raise

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

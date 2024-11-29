import os
import django
from pytest import fixture

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "API.settings")

@fixture(scope='session', autouse=True)
def django_setup():
    """Assure que Django est bien initialisé avant de lancer les tests."""
    django.setup()

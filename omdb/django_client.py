# file: omdb/django_client.py
from django.conf import settings
from omdb.client import OmdbClient

def get_client_from_settings():
    """
    Create an OmdbClient instance using OMDB_KEY from Django settings.
    """
    return OmdbClient(settings.OMDB_KEY)
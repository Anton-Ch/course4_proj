# file: movies/tasks.py
# Turn an existing function into a Celery task without tight coupling to the project name.
from celery import shared_task
from movies import omdb_integration

@shared_task
def search_and_save(search: str):
    """
    Background job:
    - Calls the original helper to fetch from OMDb and save partial Movie records
    - Safe to be called via .delay() from views
    """
    return omdb_integration.search_and_save(search)
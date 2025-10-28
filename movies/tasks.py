# file: movies/tasks.py
# Turn an existing function into a Celery task without tight coupling to the project name.
from celery import shared_task
from movies import omdb_integration

from celery import shared_task
from django.core.mail import mail_admins

@shared_task
def search_and_save(search: str):
    """
    Background job:
    - Calls the original helper to fetch from OMDb and save partial Movie records
    - Safe to be called via .delay() from views
    """
    return omdb_integration.search_and_save(search)

@shared_task
def notify_of_new_search_term(search_term: str):
    """
    Background Celery task that sends an email to site admins
    whenever a new search term is created.
    """
    mail_admins(
        subject="New Search Term",
        message=f"A new search term was used: '{search_term}'"
    )

from django.db.models.signals import post_save
from django.dispatch import receiver

from movies.models import SearchTerm

from movies.tasks import notify_of_new_search_term  # import the new Celery task

@receiver(post_save, sender=SearchTerm, dispatch_uid="search_term_saved")
def search_term_saved(sender, instance, created, **kwargs):
    """
    Called whenever a SearchTerm is saved.
    If it's a new term, trigger a Celery task to notify admins.
    """
    if created:
        # Queue the background email task
        notify_of_new_search_term.delay(instance.term)
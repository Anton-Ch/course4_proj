# file: course4_proj/celery.py
import os

from celery import Celery
from django.conf import settings

# 1) Tell Django which settings module and configuration class to use
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "course4_proj.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")

# 2) Initialize django-configurations BEFORE importing Django settings fully
import configurations
configurations.setup()

# 3) Create the Celery application instance (name = project name is a common convention)
app = Celery("course4_proj")

# 4) Load Celery-related options from Django settings with the "CELERY_" prefix
#    e.g., CELERY_BROKER_URL, CELERY_RESULT_BACKEND
app.config_from_object("django.conf:settings", namespace="CELERY")

# 5) Autodiscover tasks:
#    Celery will scan each installed app for a `tasks.py` (and sometimes `models.py`)
#    and register any @shared_task or @app.task it finds.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
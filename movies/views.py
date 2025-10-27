# file: movies/views.py
import urllib.parse

from celery.exceptions import TimeoutError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from course4_proj.celery import app          # to re-create AsyncResult later
from movies.models import Movie
from movies.tasks import search_and_save     # our Celery task

# file: movies/views.py
def search(request):
    # 1) Read input (assumes ?search_term=... is provided)
    search_term = request.GET["search_term"]

    # 2) Queue the background task (returns AsyncResult immediately)
    res = search_and_save.delay(search_term)

    # 3) Try to wait briefly (up to 2 seconds)
    try:
        res.get(timeout=2)  # if done fast (e.g., cached), we can jump straight to results
    except TimeoutError:
        # Not ready yet → send user to the waiting page with task_id
        return redirect(
            reverse("search_wait", args=(res.id,))
            + "?search_term="
            + urllib.parse.quote_plus(search_term)
        )

    # Task already finished quickly → go to results page
    return redirect(
        reverse("search_results")
        + "?search_term="
        + urllib.parse.quote_plus(search_term),
        permanent=False,
    )


def search_wait(request, result_uuid):
    # We keep passing search_term to preserve what the user searched for
    search_term = request.GET["search_term"]

    # Rebuild the AsyncResult using the UUID placed in the URL
    res = app.AsyncResult(result_uuid)

    try:
        # Immediate check (no blocking in this demo setup)
        res.get(timeout=-1)
    except TimeoutError:
        # Not ready yet → simple message (minimal demo)
        return HttpResponse("Task pending, please refresh.", status=200)

    # Finished → go see the results
    return redirect(
        reverse("search_results")
        + "?search_term="
        + urllib.parse.quote_plus(search_term)
    )


def search_results(request):
    search_term = request.GET["search_term"]

    # Simple contains filter for demo (case-insensitive)
    movies = Movie.objects.filter(title__icontains=search_term)

    # Minimal text output to prove it works
    return HttpResponse(
        "\n".join([movie.title for movie in movies]),
        content_type="text/plain",
    )
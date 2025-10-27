import logging
import re
from datetime import timedelta

from django.utils.timezone import now

# Domain models from the movies app
from movies.models import Genre, SearchTerm, Movie

# Thin Django wrapper that instantiates OmdbClient with the key from settings
from omdb.django_client import get_client_from_settings

logger = logging.getLogger(__name__)

def get_or_create_genres(genre_names):
    """
    What:
      Ensure each genre in `genre_names` has a corresponding Genre row.
      Yield the Genre instance for each name.

    Why:
      Centralize genre creation logic so other modules (views/commands) don't repeat it.
    """
    for genre_name in genre_names:
        # get_or_create prevents duplicates under concurrent calls
        genre, created = Genre.objects.get_or_create(name=genre_name)
        if created:
            logger.info("Genre created: '%s'", genre_name)
        yield genre

def fill_movie_details(movie: Movie):
    """
    What:
      Fetch a movie's full details from OMDb and persist them on the Movie record.
      If the Movie is already a full record, do nothing.

    Why:
      Encapsulate detail-fetching so both commands and views can reuse this without duplication.
    """
    if movie.is_full_record:
        logger.warning("'%s' is already a full record.", movie.title)
        return

    omdb_client = get_client_from_settings()

    # Query OMDb for full details by IMDb ID
    movie_details = omdb_client.get_by_imdb_id(movie.imdb_id)

    # Update scalar fields
    movie.title = movie_details.title
    movie.year = movie_details.year
    movie.plot = movie_details.plot
    movie.runtime_minutes = movie_details.runtime_minutes

    # Update M2M genres
    movie.genres.clear()
    for genre in get_or_create_genres(movie_details.genres):
        movie.genres.add(genre)

    # Mark as full record and save
    movie.is_full_record = True
    movie.save()
    logger.info("Movie upgraded to full record: '%s' (%s)", movie.title, movie.imdb_id)

def search_and_save(search: str):
    """
    What:
      Perform a title search against OMDb and persist partial Movie records
      (imdb_id, title, year) for each result.

      Guard condition:
        - If the same normalized search term was executed within the last 24h, skip.

    Why:
      Prevent rate-limit issues and redundant API calls.
      Provide a single place to normalize the search term and persist results.
    """
    # Normalize: collapse multiple spaces and lowercase
    normalized_search_term = re.sub(r"\s+", " ", search.lower())

    # Track last time a term was searched
    search_term, created = SearchTerm.objects.get_or_create(term=normalized_search_term)

    # If previously searched within 24 hours, skip
    if not created and (search_term.last_search > now() - timedelta(days=1)):
        logger.warning(
            "Search for '%s' was performed in the past 24 hours so not searching again.",
            normalized_search_term,
        )
        return

    omdb_client = get_client_from_settings()

    # Iterate through all pages using the client's generator
    for omdb_movie in omdb_client.search(search):
        logger.info("Saving movie: '%s' / '%s'", omdb_movie.title, omdb_movie.imdb_id)

        # Create partial Movie records idempotently
        movie, created = Movie.objects.get_or_create(
            imdb_id=omdb_movie.imdb_id,
            defaults={
                "title": omdb_movie.title,
                "year": omdb_movie.year,
            },
        )

        if created:
            logger.info("Movie created: '%s'", movie.title)

    # Touch last_search via model logic (e.g., auto_now=True) or explicitly save
    search_term.save()
    logger.info("Search term updated: '%s'", normalized_search_term)
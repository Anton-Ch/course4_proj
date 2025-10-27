# file: movies/management/commands/movie_fill.py
import logging
from django.core.management.base import BaseCommand

from movies.models import Movie
from movies.omdb_integration import fill_movie_details

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetch full details for a movie from OMDb by IMDb ID."

    def add_arguments(self, parser):
        """
        Define required argument: IMDb ID (e.g., tt1853728)
        """
        parser.add_argument("imdb_id", nargs=1)

    def handle(self, *args, **options):
        imdb_id = options["imdb_id"][0]

        try:
            # Try to find the movie in local DB
            movie = Movie.objects.get(imdb_id=imdb_id)
        except Movie.DoesNotExist:
            logger.error("Movie with IMDb ID '%s' not found.", imdb_id)
            self.stderr.write(self.style.ERROR(f"Movie not found: {imdb_id}"))
            return

        # Fill missing details from OMDb API
        fill_movie_details(movie)

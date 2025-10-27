# file: movies/management/commands/movie_search.py
from django.core.management.base import BaseCommand

# import the helper we wrote earlier
from movies.omdb_integration import search_and_save


class Command(BaseCommand):
    # short description that appears when you run `python manage.py help`
    help = "Search OMDb by title and save found movies to the database."

    def add_arguments(self, parser):
        """
        Define command-line arguments.
        'nargs="+"' means you can pass multiple words for the search term.
        Example: python manage.py movie_search django unchained
        """
        parser.add_argument("search", nargs="+")

    def handle(self, *args, **options):
        # Join all words into one search string
        search = " ".join(options["search"])
        # Run the helper function that performs the OMDb search and saves data
        search_and_save(search)
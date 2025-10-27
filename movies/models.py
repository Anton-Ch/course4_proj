# file: course4_proj/movies/models.py
from django.db import models

class SearchTerm(models.Model):
    """
    Keeps a record of each search term.
    'last_search' ensures we only re-query OMDb after 24 hours.
    """
    class Meta:
        ordering = ["id"]

	# if unique that all movie details already fetched from OMDb
    term = models.TextField(unique=True)
    last_search = models.DateTimeField(auto_now=True)  # updated automatically each save

    def __str__(self):
        return self.term


class Genre(models.Model):
    """
    Stores unique movie genres (e.g., Drama, Comedy, Sci-Fi).
    Movies can have multiple genres (Many-to-Many).
    """
    class Meta:
        ordering = ["name"]

    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    """
    Represents each movie fetched from OMDb API.
    imdb_id acts as a natural unique identifier.
    is_full_record shows whether we fetched only summary data or full details.
    """
    class Meta:
        ordering = ["title", "year"]

    title = models.TextField()
    year = models.PositiveIntegerField()
    runtime_minutes = models.PositiveIntegerField(null=True)
    # treat this as kind of like a primary key
    imdb_id = models.SlugField(unique=True)  # unique IMDb ID, e.g., 'tt0133093'
    genres = models.ManyToManyField(Genre, related_name="movies")
    plot = models.TextField(null=True, blank=True)
    # flag to determine if the `Movie` contains only the values in the list response, or if it has been supplemented with the full detail response.
    is_full_record = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.year})"
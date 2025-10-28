from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'

    def ready(self):
        # Import the signals module so Django registers all @receiver decorators
        import movies.signals  # noqa

        
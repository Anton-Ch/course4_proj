# file: omdb/client.py
import logging
import requests

# create a named logger for this module
logger = logging.getLogger(__name__)

# Base URL for all OMDb API requests
OMDB_API_URL = "https://www.omdbapi.com/"

class OmdbMovie:
    """
    Represents movie data returned from OMDb API.
    Handles validation and conversion of fields to Python types.
    """

    def __init__(self, data):
        # Data is the raw JSON/dict returned from OMDb
        self.data = data

    def check_for_detail_data_key(self, key):
        """
        Some keys exist only in detailed responses (not summary).
        Raise an exception error if trying to access missing keys.
        """
        if key not in self.data:
            raise AttributeError(
                f"{key} is not in data, please make sure this is a detail response."
            )

    # === Basic properties ===

    @property
    def imdb_id(self):
        return self.data["imdbID"]

    @property
    def title(self):
        return self.data["Title"]

    @property
    def year(self):
        # convert string "1991" to int 1991
        return int(self.data["Year"])

    # === Detail-only properties ===

    @property
    def runtime_minutes(self):
        """
        Extract runtime in minutes from the 'Runtime' string, e.g. '121 min'.
        """
        self.check_for_detail_data_key("Runtime")

        rt, units = self.data["Runtime"].split(" ")
        if units != "min":
            raise ValueError(f"Expected units 'min' for runtime, got '{units}'")

        return int(rt)

    @property
    def genres(self):
        """
        Split comma-separated genres into a Python list.
        """
        self.check_for_detail_data_key("Genre")
        return self.data["Genre"].split(", ")

    @property
    def plot(self):
        self.check_for_detail_data_key("Plot")
        return self.data["Plot"]


class OmdbClient:
    def __init__(self, api_key):
        # save OMDb API key (passed explicitly)
        self.api_key = api_key

    def make_request(self, params):
        """
        Perform a GET request, automatically appending the API key.
        """
        params["apikey"] = self.api_key

        resp = requests.get(OMDB_API_URL, params=params)
        resp.raise_for_status()  # raises an exception if HTTP error
        return resp

    def get_by_imdb_id(self, imdb_id):
        """
        Fetch a movie's full detail record by IMDB ID.
        """
        logger.info("Fetching detail for IMDB ID %s", imdb_id)
        resp = self.make_request({"i": imdb_id})
        return OmdbMovie(resp.json())

    def search(self, search):
        """
        Search for movies by title.

        Uses 'yield' to return a generator — all pages are fetched sequentially.
        """
        page = 1
        seen_results = 0
        total_results = None

        logger.info("Performing search for '%s'", search)

        while True:
            logger.info("Fetching page %d", page)
            resp = self.make_request({"s": search, "type": "movie", "page": str(page)})
            resp_body = resp.json()

            # first page contains total result count
            if total_results is None:
                total_results = int(resp_body["totalResults"])

            # yield each summary movie
            for movie in resp_body["Search"]:
                seen_results += 1
                yield OmdbMovie(movie)

            if seen_results >= total_results:
                break  # stop when all pages processed

            page += 1
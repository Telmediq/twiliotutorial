import requests
from django.conf import settings
import logging
import urllib.parse
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Beer:

    # Gets a random beer from the API. Returns some data.
    def get_beer_fact(self):

        params = {
            'key': settings.BEER_API_KEY

        }
        path = "/v2/beer/random"
        url = urllib.parse.urljoin(settings.BEER_API_URL, path)
        response = requests.get(url=url, params=params)
        response.close()
        if response.status_code != 200:
            logging.debug(f"Response code: {response.status_code}")

        response_dict = json.loads(response.content)

        logging.debug(f"Beer response: {response_dict}")
        return response_dict['data']


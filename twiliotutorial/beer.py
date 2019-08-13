import json
import logging
import urllib.parse
from collections import namedtuple
from json import JSONDecodeError
from typing import Dict, Optional

import requests
from django.conf import settings

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

RANDOM_BEER_URI = "/v2/beer/random"
BEER_URI = "/v2/beers"

BeerFact = namedtuple('Beerfact', 'id name abv ibu style')


class Beer:
    @staticmethod
    def get_beer_url() -> str:
        return urllib.parse.urljoin(settings.BEER_API_URL, RANDOM_BEER_URI)

    @staticmethod
    def get_beer_with_id_url() -> str:
        return urllib.parse.urljoin(settings.BEER_API_URL, BEER_URI)

    @staticmethod
    def get_beer_fact_from_api(url: str, params: Optional[Dict[str, str]]) -> Dict[str, str]:
        response = requests.get(url=url, params=params)
        response.close()
        result = dict()
        if response.status_code != 200:
            logging.debug("Response code: %s", response.status_code)
            return result
        try:
            result = json.loads(response.content)
        except JSONDecodeError as e:
            logging.debug("Could not parse JSON from Beer API %s", response.content)
        logging.debug("Beer response: %s", response.status_code)
        return result

    @staticmethod
    def convert_result_to_beer_fact(result) -> BeerFact:
        if 'currentPage' in result:
            data = result.get('data')[0]
        else:
            data = result.get('data')

        if not data or 'name' not in data or 'id' not in data:
            return BeerFact(id=None, name=None, abv=None, style=None, ibu=None)
        return BeerFact(id=data.get('id'), name=data.get('name'), abv=data.get('abv'), style=data.get('style'),
                        ibu=data.get('ibu'))

    # Gets a random beer from the API. Returns some data.
    def get_random_beer_fact(self) -> BeerFact:
        logging.debug("Getting a random beer fact")
        params = {
            'key': settings.BEER_API_KEY
        }
        url = self.get_beer_url()
        result = self.get_beer_fact_from_api(url, params)

        return self.convert_result_to_beer_fact(result)

    # Get a specific beer from the API by ID. Returns some data.
    def get_beer_by_id(self, beerid) -> BeerFact:
        logging.debug("Looking for beer id: %s", beerid)
        params = {
            'key': settings.BEER_API_KEY,
            'ids': beerid
        }

        url = self.get_beer_with_id_url()
        result = self.get_beer_fact_from_api(url, params)
        # Getting a beer by ID returns a paginated list. Let's grab the first item only
        return self.convert_result_to_beer_fact(result)

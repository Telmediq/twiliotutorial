import json
from unittest import mock
from unittest.mock import call

from django.conf import settings
from django.test import SimpleTestCase

from twiliotutorial.beer import Beer, BeerFact


class BeerTestCase(SimpleTestCase):
    """Test Beer class methods. Since we dont have a Database, use SimpleTestCase"""

    def test__get_random_beer_url__returns_url(self):
        expected_url = 'https://sandbox-api.brewerydb.com/v2/beer/random'
        beer = Beer()
        url = beer.get_random_beer_url()

        self.assertEqual(url, expected_url)

    def test__get_beer_with_id_url__returns_url(self):
        expected_url = 'https://sandbox-api.brewerydb.com/v2/beers'
        beer = Beer()
        url = beer.get_beer_with_id_url()

        self.assertEqual(url, expected_url)

    @mock.patch('twiliotutorial.beer.requests')
    def test__get_beer_fact_from_api__returns_beer_fact(self, mock_requests):
        expected_result = json.dumps({
            'data': {
                'name': 'test',
                'id': 'test_id',
                'abv': '1.0',
                'ibu': 99,
                'style': {'description': 'test_description'}
            }
        })
        mock_result = mock.Mock()
        mock_result.status_code = 200
        mock_result.content = expected_result
        mock_requests.get.return_value = mock_result

        beer = Beer()

        result = beer.get_beer_fact_from_api('http://some/url', {'some': 'param'})

        self.assertEqual(result, json.loads(expected_result))

    @mock.patch('twiliotutorial.beer.requests')
    def test__get_beer_fact_from_api__status_non_200__returns_empty_result(self, mock_requests):
        mock_result = mock.Mock()
        mock_result.status_code = 404
        mock_requests.get.return_value = mock_result

        beer = Beer()

        result = beer.get_beer_fact_from_api('http://some/url', {'some': 'param'})

        self.assertEqual(result, {})

    @mock.patch('twiliotutorial.beer.requests')
    def test__get_beer_fact_from_api__content_not_json__returns_empty_result(self, mock_requests):
        bad_json = 'foo: bar, [waz, foop]'
        mock_result = mock.Mock()
        mock_result.status_code = 200
        mock_result.content = bad_json
        mock_requests.get.return_value = mock_result

        beer = Beer()

        result = beer.get_beer_fact_from_api('http://some/url', {'some': 'param'})

        self.assertEqual(result, {})

    def test__convert_result_to_beer_fact__paginated__returns_first_result_as_beer_fact(self):
        mock_api_response_data = {
            'currentPage': 1,
            'data': [{
                'name': 'test',
                'id': 'test_id',
                'abv': '1.0',
                'ibu': 99,
                'style': {'description': 'test_description'}
            }, ]
        }
        data = mock_api_response_data['data'][0]
        expected_beer_fact = BeerFact(id=data.get('id'), name=data.get('name'), abv=data.get('abv'),
                                      style=data.get('style'),
                                      ibu=data.get('ibu'))
        beer = Beer()

        result = beer.convert_result_to_beer_fact(mock_api_response_data)

        self.assertEqual(result, expected_beer_fact)

    def test__convert_result_to_beer_fact__nonpaginated__returns_result_as_beer_fact(self):
        mock_api_response_data = {
            'data': {
                'name': 'test',
                'id': 'test_id',
                'abv': '1.0',
                'ibu': 99,
                'style': {'description': 'test_description'}
            }
        }
        data = mock_api_response_data['data']
        expected_beer_fact = BeerFact(id=data.get('id'), name=data.get('name'), abv=data.get('abv'),
                                      style=data.get('style'),
                                      ibu=data.get('ibu'))
        beer = Beer()

        result = beer.convert_result_to_beer_fact(mock_api_response_data)

        self.assertEqual(result, expected_beer_fact)

    def test__convert_result_to_beer_fact__no_data__returns_empty_beer_fact(self):
        expected_beer_fact = BeerFact(id=None, name=None, abv=None, style=None, ibu=None)
        mock_api_response_data = {}
        beer = Beer()
        result = beer.convert_result_to_beer_fact(mock_api_response_data)

        self.assertEqual(result, expected_beer_fact)

    def test__convert_result_to_beer_fact__data_empty__returns_empty_beer_fact(self):
        expected_beer_fact = BeerFact(id=None, name=None, abv=None, style=None, ibu=None)
        mock_api_response_data = {
            'data': None
        }
        beer = Beer()
        result = beer.convert_result_to_beer_fact(mock_api_response_data)

        self.assertEqual(result, expected_beer_fact)

    def test__convert_result_to_beer_fact__no_id__returns_empty_beer_fact(self):
        expected_beer_fact = BeerFact(id=None, name=None, abv=None, style=None, ibu=None)
        mock_api_response_data = {
            'data': {'name': 'test_name'}
        }
        beer = Beer()
        result = beer.convert_result_to_beer_fact(mock_api_response_data)

        self.assertEqual(result, expected_beer_fact)

    def test__convert_result_to_beer_fact__no_name__returns_empty_beer_fact(self):
        expected_beer_fact = BeerFact(id=None, name=None, abv=None, style=None, ibu=None)
        mock_api_response_data = {
            'data': {'id': 'test_id'}
        }
        beer = Beer()
        result = beer.convert_result_to_beer_fact(mock_api_response_data)

        self.assertEqual(result, expected_beer_fact)

    @mock.patch('twiliotutorial.beer.Beer.get_random_beer_url')
    @mock.patch('twiliotutorial.beer.Beer.get_beer_fact_from_api')
    def test__get_random_beer_fact__calls_get_beer_fact_from_api_with_params__returns_expected_beer_fact(self,
                                                                                                         mock_get,
                                                                                                         mock_url):
        expected_data = {
            'data': {
                'name': 'test',
                'id': 'test_id',
                'abv': '1.0',
                'ibu': 99,
                'style': {'description': 'test_description'}
            }
        }
        data = expected_data.get('data')
        expected_beer_fact = BeerFact(id=data.get('id'), name=data.get('name'), abv=data.get('abv'),
                                      style=data.get('style'),
                                      ibu=data.get('ibu'))
        mock_get.return_value = expected_data
        mock_url.return_value = 'http:/useless.org'
        beer = Beer()
        beer_fact = beer.get_random_beer_fact()

        self.assertEqual(beer_fact, expected_beer_fact)
        self.assertEqual(mock_get.call_args_list[0], call(url=mock_url(), params={'key': settings.BEER_API_KEY}))

    @mock.patch('twiliotutorial.beer.Beer.get_beer_with_id_url')
    @mock.patch('twiliotutorial.beer.Beer.get_beer_fact_from_api')
    def test__get_beer_by_id__calls_get_beer_fact_from_api_with_params__returns_expected_beer_fact(self,
                                                                                                   mock_get,
                                                                                                   mock_url):
        expected_data = {
            'currentPage': 1,
            'data': [{
                'name': 'test',
                'id': 'test_id',
                'abv': '1.0',
                'ibu': 99,
                'style': {'description': 'test_description'}
            }, ]
        }
        data = expected_data.get('data')[0]
        expected_beer_fact = BeerFact(id=data.get('id'), name=data.get('name'), abv=data.get('abv'),
                                      style=data.get('style'),
                                      ibu=data.get('ibu'))
        mock_get.return_value = expected_data
        mock_url.return_value = 'http:/useless.org'
        beer = Beer()
        beer_fact = beer.get_beer_by_id('test_id')

        self.assertEqual(beer_fact, expected_beer_fact)
        self.assertEqual(mock_get.call_args_list[0],
                         call(url=mock_url(), params={'key': settings.BEER_API_KEY, 'ids': 'test_id'}))

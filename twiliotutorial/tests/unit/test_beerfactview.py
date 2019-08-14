from unittest import mock

from django.test import SimpleTestCase, RequestFactory

from twiliotutorial.beer import BeerFact
from twiliotutorial.views import BeerFactView


class BeerFactViewTestCase(SimpleTestCase):
    """Test BeerFactView class. Since we dont have a Database, use SimpleTestCase"""

    def test__build_response__populated_beer_fact__returns_populated_voice_response(self):
        beer_fact = BeerFact(name='test', id='test_1', abv=1.0, ibu=99, style=dict(description='test_description'))
        view = BeerFactView()
        response = view.build_response(beer_fact)

        expected_response = '<?xml version="1.0" encoding="UTF-8"?>' \
                            '<Response>' \
                            '<Say voice="Polly.Brian">Hello! I am going to drop a dank beer on you.</Say>' \
                            '<Gather action="/beertext?beerid=test_1" actionOnEmptyResult="false" ' \
                            'finishOnKey="" numDigits="1" timeout="200">' \
                            '<Say voice="Polly.Brian">Our beer today is test</Say>' \
                            '<Say voice="Polly.Brian">Coming in at 1.0 percent.</Say>' \
                            '<Say voice="Polly.Brian">test_description</Say></Gather>' \
                            '<Say voice="Polly.Brian">Wow! You made it to the end. Be excellent to each other.</Say>' \
                            '<Hangup />' \
                            '</Response>'

        self.assertEqual(response.to_xml(), expected_response)

    def test__build_response__populated_beer_fact_missing_abv__returns_populated_voice_response(self):
        beer_fact = BeerFact(name='test', id='test_1', abv=None, ibu=99, style=dict(description='test_description'))
        view = BeerFactView()
        response = view.build_response(beer_fact)

        expected_response = '<?xml version="1.0" encoding="UTF-8"?>' \
                            '<Response>' \
                            '<Say voice="Polly.Brian">Hello! I am going to drop a dank beer on you.</Say>' \
                            '<Gather action="/beertext?beerid=test_1" actionOnEmptyResult="false" ' \
                            'finishOnKey="" numDigits="1" timeout="200">' \
                            '<Say voice="Polly.Brian">Our beer today is test</Say>' \
                            '<Say voice="Polly.Brian">test_description</Say>' \
                            '</Gather>' \
                            '<Say voice="Polly.Brian">Wow! You made it to the end. Be excellent to each other.</Say>' \
                            '<Hangup />' \
                            '</Response>'

        self.assertEqual(response.to_xml(), expected_response)

    def test__build_response__populated_beer_fact_missing_style__returns_populated_voice_response(self):
        beer_fact = BeerFact(name='test', id='test_1', abv=1.0, ibu=99, style=None)
        view = BeerFactView()
        response = view.build_response(beer_fact)

        expected_response = '<?xml version="1.0" encoding="UTF-8"?>' \
                            '<Response>' \
                            '<Say voice="Polly.Brian">Hello! I am going to drop a dank beer on you.</Say>' \
                            '<Gather action="/beertext?beerid=test_1" actionOnEmptyResult="false" ' \
                            'finishOnKey="" numDigits="1" timeout="200">' \
                            '<Say voice="Polly.Brian">Our beer today is test</Say>' \
                            '<Say voice="Polly.Brian">Coming in at 1.0 percent.</Say>' \
                            '</Gather>' \
                            '<Say voice="Polly.Brian">Wow! You made it to the end. Be excellent to each other.</Say>' \
                            '<Hangup />' \
                            '</Response>'

        self.assertEqual(response.to_xml(), expected_response)

    def test__build_response__populated_beer_fact_missing_style_description__returns_populated_voice_response(self):
        beer_fact = BeerFact(name='test', id='test_1', abv=None, ibu=99, style=dict())
        view = BeerFactView()
        response = view.build_response(beer_fact)

        expected_response = '<?xml version="1.0" encoding="UTF-8"?>' \
                            '<Response>' \
                            '<Say voice="Polly.Brian">Hello! I am going to drop a dank beer on you.</Say>' \
                            '<Gather action="/beertext?beerid=test_1" actionOnEmptyResult="false" ' \
                            'finishOnKey="" numDigits="1" timeout="200">' \
                            '<Say voice="Polly.Brian">Our beer today is test</Say>' \
                            '</Gather>' \
                            '<Say voice="Polly.Brian">Wow! You made it to the end. Be excellent to each other.</Say>' \
                            '<Hangup />' \
                            '</Response>'

        self.assertEqual(response.to_xml(), expected_response)

    @mock.patch('twiliotutorial.views.Beer.get_random_beer_fact', autospec=True)
    def test__get_beer_fact__returns_beer_fact(self, mock_random_beer_fact):
        expected_beer_fact = BeerFact(name='test', id='test_1', abv=1.0, ibu=99,
                                      style=dict(description='test_description'))

        mock_random_beer_fact.return_value = expected_beer_fact
        view = BeerFactView()
        beer_fact = view.get_beer_fact()
        self.assertEqual(beer_fact, expected_beer_fact)

    @mock.patch('twiliotutorial.views.Beer.get_random_beer_fact', autospec=True)
    def test__post__request_with_valid_query_params__returns_content_type_text_xml(self, mock_random_beer_fact):
        expected_beer_fact = BeerFact(name='test', id='test_1', abv=1.0, ibu=99,
                                      style=dict(description='test_description'))

        mock_random_beer_fact.return_value = expected_beer_fact

        rf = RequestFactory()
        request = rf.post({'beerid': 'test_id'})

        view = BeerFactView()
        response = view.post(request)

        self.assertEqual(response._headers.get('content-type'), ('Content-Type', 'text/xml'))

    @mock.patch('twiliotutorial.views.Beer.get_random_beer_fact', autospec=True)
    @mock.patch('twiliotutorial.views.BeerFactView.build_response', autospec=True)
    def test__post__request_with_valid_query_params__returns_expected_content(self, mock_build_response,
                                                                              mock_random_beer_fact):
        expected_beer_fact = BeerFact(name='test', id='test_1', abv=1.0, ibu=99,
                                      style=dict(description='test_description'))

        expected_response_data = b'It worked!'
        mock_response = mock.Mock()
        mock_response.to_xml.return_value = expected_response_data
        mock_build_response.return_value = mock_response
        mock_random_beer_fact.return_value = expected_beer_fact

        rf = RequestFactory()
        request = rf.post('/some/path/')


        view = BeerFactView()
        response = view.post(request)

        self.assertEqual(response.content, expected_response_data)

from unittest import mock

from django.test import SimpleTestCase, RequestFactory

from twiliotutorial.beer import BeerFact
from twiliotutorial.views import BeerTextView


class BeerTextViewTestCase(SimpleTestCase):
    """Test BeerTextView class. Since we dont have a Database, use SimpleTestCase"""

    def setUp(self) -> None:
        self.beer_fact = BeerFact(name='test', id='test_1', abv=1.0, ibu=99,
                                  style=dict(description='test_description'))

    def test__create_text_body(self):
        view = BeerTextView()
        text_body = view.create_text_body(self.beer_fact)
        expected_text_body = f'Hi there! You were listening to: {self.beer_fact.name}, {self.beer_fact.abv}%, IBU: {self.beer_fact.ibu}'
        self.assertEqual(text_body, expected_text_body)

    @mock.patch('twiliotutorial.views.Client', autospec=True)
    def test__text_beer_info_to_number__populated_beer_fact__calls_message_creat_with_args(self, mock_twilio_client):
        assertable_mock = mock.Mock()
        mock_twilio_client.return_value = assertable_mock
        from_ = '5551234'
        to_ = '8675309'

        view = BeerTextView()
        view.text_beer_info_to_number(beer_fact=self.beer_fact, from_=from_, to_=to_)
        self.assertEqual(assertable_mock.messages.create.call_args_list[0],
                         mock.call(body='Hi there! You were listening to: test, 1.0%, IBU: 99', from_='8675309',
                                   to='5551234'))

    @mock.patch('twiliotutorial.views.Client', autospec=True)
    def test__text_beer_info_to_number__populated_beer_fact_no_abv__calls_message_creat_with_args(self,
                                                                                                  mock_twilio_client):
        assertable_mock = mock.Mock()
        mock_twilio_client.return_value = assertable_mock
        beer_fact = BeerFact(name='test', id='test_1', abv=None, ibu=99, style=dict(description='test_description'))
        from_ = '5551234'
        to_ = '8675309'

        view = BeerTextView()
        view.text_beer_info_to_number(beer_fact=beer_fact, from_=from_, to_=to_)
        self.assertTrue(assertable_mock.messages.create.call_args_list[0],
                        mock.call(body='Hi there! You were listening to: test, Unknown, IBU: 99', from_='8675309',
                                  to='5551234'))

    @mock.patch('twiliotutorial.views.Client', autospec=True)
    def test__text_beer_info_to_number__populated_beer_fact_no_ibu__calls_message_creat_with_args(self,
                                                                                                  mock_twilio_client):
        assertable_mock = mock.Mock()
        mock_twilio_client.return_value = assertable_mock
        beer_fact = BeerFact(name='test', id='test_1', abv=None, ibu=99, style=dict(description='test_description'))
        from_ = '5551234'
        to_ = '8675309'

        view = BeerTextView()
        view.text_beer_info_to_number(beer_fact=beer_fact, from_=from_, to_=to_)
        self.assertTrue(assertable_mock.messages.create.call_args_list[0],
                        mock.call(body='Hi there! You were listening to: test, 1.0%, IBU: Unknown', from_='8675309',
                                  to='5551234'))

    @mock.patch('twiliotutorial.views.Beer.get_beer_by_id', autospec=True)
    def test__get_beer_fact__returns_beer_fact(self, mock_random_beer_fact):
        mock_random_beer_fact.return_value = self.beer_fact
        view = BeerTextView()
        beer_fact = view.get_beer_fact_for_beer_id('test_1')
        self.assertEqual(beer_fact, self.beer_fact)

    @mock.patch('twiliotutorial.views.BeerTextView.text_beer_info_to_number', autospec=True)
    @mock.patch('twiliotutorial.views.BeerTextView.get_beer_fact_for_beer_id', autospec=True)
    def test__post__request_with_missing_from_param__doesnt_call_text_beer_info__returns_expected_content(self,
                                                                                                          get_beer_fact_for_beer_id,
                                                                                                          mock_text_beer_info_to_number):
        expected_response_data = b'<?xml version="1.0" encoding="UTF-8"?><Response />'
        get_beer_fact_for_beer_id.return_value = self.beer_fact

        rf = RequestFactory()
        request = rf.post('test/path', {'To': '5551234'},
                          QUERY_STRING='beerid=test_id')

        view = BeerTextView()
        response = view.post(request)
        self.assertFalse(mock_text_beer_info_to_number.called)
        self.assertEqual(response.content, expected_response_data)

    @mock.patch('twiliotutorial.views.BeerTextView.text_beer_info_to_number', autospec=True)
    @mock.patch('twiliotutorial.views.BeerTextView.get_beer_fact_for_beer_id', autospec=True)
    def test__post__request_with_missing_beerid_query_param__doesnt_call_text_beer_info__returns_expected_content(self,
                                                                                                                  get_beer_fact_for_beer_id,
                                                                                                                  mock_text_beer_info_to_number):
        expected_response_data = b'<?xml version="1.0" encoding="UTF-8"?><Response />'
        get_beer_fact_for_beer_id.return_value = self.beer_fact

        rf = RequestFactory()
        request = rf.post('test/path', {'To': '5551234', 'From': '8675309'})

        view = BeerTextView()
        response = view.post(request)
        self.assertFalse(mock_text_beer_info_to_number.called)
        self.assertEqual(response.content, expected_response_data)

    @mock.patch('twiliotutorial.views.BeerTextView.text_beer_info_to_number', autospec=True)
    @mock.patch('twiliotutorial.views.BeerTextView.get_beer_fact_for_beer_id', autospec=True)
    def test__post__request_with_valid_query_params__calls_text_beer_info_to_number_with_params_returns_content(self,
                                                                                                                get_beer_fact_for_beer_id,
                                                                                                                mock_text_beer_info_to_number):
        expected_response_data = b'<?xml version="1.0" encoding="UTF-8"?><Response />'
        get_beer_fact_for_beer_id.return_value = self.beer_fact

        rf = RequestFactory()
        request = rf.post('test/path', {'From': '8675309', 'To': '5551234'},
                          QUERY_STRING='beerid=test_id')
        view = BeerTextView()
        response = view.post(request)

        self.assertEqual(mock_text_beer_info_to_number.call_args_list[0],
                         mock.call(view, beer_fact=self.beer_fact, from_='8675309',
                                   to_='5551234'))
        self.assertEqual(response.content, expected_response_data)

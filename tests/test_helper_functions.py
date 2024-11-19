import unittest
from unittest.mock import patch, Mock
import requests
from src.helper_functions import get_login_page, login, access_amenity_reservations, make_tennis_court_reservation

class TestHelperFunctions(unittest.TestCase):

    @patch('src.helper_functions.requests.Session.get')
    def test_get_login_page_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<input name="__RequestVerificationToken" value="dummy_token">'
        mock_get.return_value = mock_response

        session = requests.Session()
        csrf_token = get_login_page(session, "http://dummyurl.com/login")
        self.assertEqual(csrf_token, "dummy_token")

    @patch('src.helper_functions.requests.Session.get')
    def test_get_login_page_no_token(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<input name="some_other_field" value="no_token">'
        mock_get.return_value = mock_response

        session = requests.Session()
        csrf_token = get_login_page(session, "http://dummyurl.com/login")
        self.assertIsNone(csrf_token)

    @patch('src.helper_functions.requests.Session.get')
    def test_get_login_page_failure(self, mock_get):
        mock_get.side_effect = Exception("Connection error")

        session = requests.Session()
        csrf_token = get_login_page(session, "http://dummyurl.com/login")
        self.assertIsNone(csrf_token)

    @patch('src.helper_functions.requests.Session.post')
    def test_login_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 302
        mock_post.return_value = mock_response

        session = requests.Session()
        result = login(session, "http://dummyurl.com/login", "user", "pass", "dummy_token")
        self.assertTrue(result)

    @patch('src.helper_functions.requests.Session.post')
    def test_login_failure(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        session = requests.Session()
        result = login(session, "http://dummyurl.com/login", "user", "pass", "dummy_token")
        self.assertFalse(result)

    @patch('src.helper_functions.requests.Session.post')
    def test_login_exception(self, mock_post):
        mock_post.side_effect = Exception("Post request failed")

        session = requests.Session()
        result = login(session, "http://dummyurl.com/login", "user", "pass", "dummy_token")
        self.assertFalse(result)

    @patch('src.helper_functions.requests.Session.get')
    def test_access_amenity_reservations_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        session = requests.Session()
        result = access_amenity_reservations(session)
        self.assertTrue(result)

    @patch('src.helper_functions.requests.Session.get')
    def test_access_amenity_reservations_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        session = requests.Session()
        result = access_amenity_reservations(session)
        self.assertFalse(result)

    @patch('src.helper_functions.requests.Session.get')
    def test_access_amenity_reservations_exception(self, mock_get):
        mock_get.side_effect = Exception("Get request failed")

        session = requests.Session()
        result = access_amenity_reservations(session)
        self.assertFalse(result)

    @patch('src.helper_functions.requests.Session.post')
    @patch('src.helper_functions.requests.Session.get')
    def test_make_tennis_court_reservation_success(self, mock_get, mock_post):
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        session = requests.Session()
        result = make_tennis_court_reservation(session, "2024-10-20", "07:00 AM")
        self.assertTrue(result)

    @patch('src.helper_functions.requests.Session.post')
    @patch('src.helper_functions.requests.Session.get')
    def test_make_tennis_court_reservation_failure(self, mock_get, mock_post):
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        mock_post_response = Mock()
        mock_post_response.status_code = 400
        mock_post.return_value = mock_post_response

        session = requests.Session()
        result = make_tennis_court_reservation(session, "2024-10-20", "07:00 AM")
        self.assertFalse(result)

    @patch('src.helper_functions.requests.Session.post')
    @patch('src.helper_functions.requests.Session.get')
    def test_make_tennis_court_reservation_exception(self, mock_get, mock_post):
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        mock_post.side_effect = Exception("Post request failed")

        session = requests.Session()
        result = make_tennis_court_reservation(session, "2024-10-20", "07:00 AM")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
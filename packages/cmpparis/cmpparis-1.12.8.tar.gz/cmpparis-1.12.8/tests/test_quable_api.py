import requests
import unittest
from unittest.mock import patch, Mock
from cmpparis.quable_api import QuableAPI

class TestQuableAPI(unittest.TestCase):
    def setUp(self):
        self.quable_api = QuableAPI()

    @patch('cmpparis.quable_api.requests.get')
    def test_get(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = self.quable_api.get('test_endpoint')
        self.assertEqual(response, {'data': 'test_data'})
        mock_get.assert_called_once_with(f'{self.quable_api.base_url}/test_endpoint', headers=self.quable_api.headers, params=None)

    @patch('cmpparis.quable_api.requests.get')
    def test_get_with_params(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        params = {'param1': 'value1', 'param2': 'value2'}
        response = self.quable_api.get('test_endpoint', params=params)
        self.assertEqual(response, {'data': 'test_data'})
        mock_get.assert_called_once_with(f'{self.quable_api.base_url}/test_endpoint', headers=self.quable_api.headers, params=params)

    @patch('cmpparis.quable_api.requests.post')
    def test_post(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {'data': 'test_data'}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        data = {'key': 'value'}
        response = self.quable_api.post('test_endpoint', data)
        self.assertEqual(response, {'data': 'test_data'})
        mock_post.assert_called_once_with(f'{self.quable_api.base_url}/test_endpoint', headers=self.quable_api.headers, json=data)

if __name__ == '__main__':
    unittest.main()
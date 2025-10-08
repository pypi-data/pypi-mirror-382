import unittest
from unittest.mock import Mock, patch
import io
from cmpparis.sharepoint import Sharepoint

class TestSharepoint(unittest.TestCase):

    def setUp(self):
        self.site_url = "https://example.sharepoint.com"
        self.site_path = "sites/testsite"
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.sharepoint = Sharepoint(self.site_url, self.site_path, self.client_id, self.client_secret)

    @patch('cmpparis.sharepoint.ClientContext')
    @patch('cmpparis.sharepoint.ClientCredential')
    def test_init(self, mock_client_credential, mock_client_context):
        mock_client_context.return_value.with_credentials.return_value = "mocked_context"
        
        sharepoint = Sharepoint(self.site_url, self.site_path, self.client_id, self.client_secret)
        
        mock_client_context.assert_called_once_with(f"{self.site_url}/{self.site_path}")
        mock_client_credential.assert_called_once_with(self.client_id, self.client_secret)
        mock_client_context.return_value.with_credentials.assert_called_once_with(mock_client_credential.return_value)
        self.assertEqual(sharepoint.ctx, "mocked_context")

    def test_get_files(self):
        self.sharepoint.ctx = Mock()
        mock_folder = Mock()
        mock_files = Mock()

        self.sharepoint.ctx.web.get_folder_by_server_relative_url.return_value = mock_folder
        mock_folder.files = mock_files

        result = self.sharepoint.get_files("/test/folder")

        self.sharepoint.ctx.web.get_folder_by_server_relative_url.assert_called_once_with("/test/folder")
        self.sharepoint.ctx.load.assert_called_once_with(mock_files)
        self.sharepoint.ctx.execute_query.assert_called_once()
        self.assertEqual(result, mock_files)

    @patch('cmpparis.sharepoint.SharePointFile.open_binary')
    def test_read_file(self, mock_open_binary):
        mock_response = Mock()
        mock_response.content = b"test content"
        mock_open_binary.return_value = mock_response

        result = self.sharepoint.read_file("/test/file.txt")

        mock_open_binary.assert_called_once_with(self.sharepoint.ctx, "/test/file.txt")
        self.assertIsInstance(result, io.BytesIO)
        self.assertEqual(result.getvalue(), b"test content")

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=b"test content")
    def test_upload_file(self, mock_open):
        self.sharepoint.ctx = Mock()
        mock_folder = Mock()
        
        self.sharepoint.ctx.web.get_folder_by_server_relative_url.return_value = mock_folder

        self.sharepoint.upload_file("/test/folder", "test.txt")

        self.sharepoint.ctx.web.get_folder_by_server_relative_url.assert_called_once_with("/test/folder")
        mock_open.assert_called_once_with("test.txt", "rb")
        mock_folder.upload_file.assert_called_once_with("test.txt", b"test content")
        mock_folder.upload_file.return_value.execute_query.assert_called_once()

if __name__ == '__main__':
    unittest.main()
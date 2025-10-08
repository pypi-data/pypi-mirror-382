import unittest
from unittest.mock import patch, MagicMock
from cmpparis.ses_utils import send_email_to_support, send_email

class TestSESUtils(unittest.TestCase):

    @patch('cmpparis.ses_utils.get_parameter')
    @patch('cmpparis.ses_utils.send_email')
    def test_send_email_to_support(self, mock_send_email, mock_get_parameter):
        # Arrange
        mock_get_parameter.side_effect = [
            'from@example.com',  # Mocking the from_email
            'support@example.com'  # Mocking the to_email
        ]
        
        subject = "Test Subject"
        content = "Test Content"

        # Act
        send_email_to_support(subject, content)

        # Assert
        mock_get_parameter.assert_any_call('generic', 'technical_report_email')
        mock_get_parameter.assert_any_call('generic', 'to_support_email')
        
        mock_send_email.assert_called_once_with(
            'from@example.com',
            'support@example.com',
            subject,
            content,
            []
        )

    @patch('cmpparis.ses_utils.get_region_name')
    @patch('cmpparis.ses_utils.boto3.client')
    def test_send_email_success(self, mock_boto3_client, mock_get_region_name):
        mock_get_region_name.return_value = 'us-west-2'
        mock_ses_client = MagicMock()
        mock_boto3_client.return_value = mock_ses_client
        mock_ses_client.send_raw_email.return_value = {'MessageId': '123456789'}

        response = send_email('from@example.com', 'to@example.com', 'Test Subject', 'Test Content')

        mock_get_region_name.assert_called_once()
        mock_boto3_client.assert_called_once_with('ses', region_name='us-west-2')
        mock_ses_client.send_raw_email.assert_called_once()
        self.assertEqual(response, {'MessageId': '123456789'})

    @patch('cmpparis.ses_utils.get_region_name')
    @patch('cmpparis.ses_utils.boto3.client')
    def test_send_email_with_attachments(self, mock_boto3_client, mock_get_region_name):
        mock_get_region_name.return_value = 'us-west-2'
        mock_ses_client = MagicMock()
        mock_boto3_client.return_value = mock_ses_client
        mock_ses_client.send_raw_email.return_value = {'MessageId': '123456789'}

        response = send_email('from@example.com', 'to@example.com', 'Test Subject', 'Test Content', ['test.txt'])

        mock_get_region_name.assert_called_once()
        mock_boto3_client.assert_called_once_with('ses', region_name='us-west-2')
        mock_ses_client.send_raw_email.assert_called_once()
        self.assertEqual(response, {'MessageId': '123456789'})

if __name__ == '__main__':
    unittest.main()
import unittest
import boto3
import os
from moto import mock_aws
from unittest.mock import patch, Mock
from cmpparis.s3 import S3

class TestS3(unittest.TestCase):
    @mock_aws
    def setUp(self):
        self.mock_aws = mock_aws()
        self.mock_aws.start()
        
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.s3.create_bucket(Bucket='XXXXXXXXXXX')
        self.s3_obj = S3('us-east-1', 'XXXXXXXXXXX')

    def tearDown(self):
        self.mock_aws.stop()

    @patch('cmpparis.ses_utils.send_email_to_support')
    def test_download_file_from_s3(self, mock_send_email):
        with mock_aws():
            self.s3.put_object(Bucket='XXXXXXXXXXX', Key='test.txt', Body=b'test content')
            local_filename = 'test.txt'
            self.assertTrue(self.s3_obj.download_file_from_s3('test.txt', local_filename))
            mock_send_email.assert_not_called()

    @patch('cmpparis.ses_utils.send_email_to_support')
    def test_get_file_from_s3(self, mock_send_email):
        with mock_aws():
            self.s3.put_object(Bucket='XXXXXXXXXXX', Key='test.txt', Body=b'test content')
            content = self.s3_obj.get_file_from_s3('test.txt')
            self.assertEqual(content, 'test content')
            mock_send_email.assert_not_called()

    @patch('cmpparis.ses_utils.send_email_to_support')
    def test_get_files_from_s3(self, mock_send_email):
        with mock_aws():
            self.s3.put_object(Bucket='XXXXXXXXXXX', Key='test1.txt', Body=b'test content 1')
            self.s3.put_object(Bucket='XXXXXXXXXXX', Key='test2.txt', Body=b'test content 2')
            files = self.s3_obj.get_files_from_s3('test')
            self.assertEqual(len(files), 2)
            self.assertIn('test1.txt', files)
            self.assertIn('test2.txt', files)
            mock_send_email.assert_not_called()

    @patch('cmpparis.ses_utils.send_email_to_support')
    def test_upload_file_to_s3(self, mock_send_email):
        with mock_aws():
            with open('test.txt', 'w') as f:
                f.write('test content')
            self.assertTrue(self.s3_obj.upload_file_to_s3('test.txt', 'test.txt'))
            body = self.s3.get_object(Bucket='XXXXXXXXXXX', Key='test.txt')['Body'].read().decode('utf-8')
            self.assertEqual(body, 'test content')
            mock_send_email.assert_not_called()

    @patch('cmpparis.ses_utils.send_email_to_support')
    def test_delete_file_from_s3(self, mock_send_email):
        with mock_aws():
            self.s3.put_object(Bucket='XXXXXXXXXXX', Key='test.txt', Body=b'test content')
            self.assertTrue(self.s3_obj.delete_file_from_s3('test.txt'))
            objects = self.s3.list_objects_v2(Bucket='XXXXXXXXXXX')
            self.assertEqual('Contents' not in objects.keys(), True)
            mock_send_email.assert_not_called()

    @patch('cmpparis.ses_utils.send_email_to_support')
    def test_archive_file_in_s3(self, mock_send_email):
        with mock_aws():
            self.s3.put_object(Bucket='XXXXXXXXXXX', Key='/folder/test.txt', Body=b'test content')
            is_archived = self.s3_obj.archive_file_in_s3('/folder', '/folder/test.txt')
            objects = self.s3_obj.get_files_from_s3('archive')

            self.assertTrue(is_archived)
            self.assertEqual(len([obj for obj in objects if 'folder' in obj]) > 0, True)
            mock_send_email.assert_not_called()

if __name__ == '__main__':
    unittest.main()
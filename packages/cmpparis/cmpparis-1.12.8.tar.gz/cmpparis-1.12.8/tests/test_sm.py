import boto3
import os
import unittest
import boto3.session
from moto import mock_aws
from cmpparis.sm_utils import *

class TestSSM(unittest.TestCase):

    @mock_aws
    def setUp(self):
        self.mock_aws = mock_aws()
        self.mock_aws.start()
        self.region_name = 'eu-west-1'

        os.environ['AWS_DEFAULT_REGION'] = self.region_name
        os.environ['AWS_ACCESS_KEY_ID'] = 'test'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'

        session = boto3.session.Session()
        self.ssm_client = session.client(service_name='secretsmanager', region_name=self.region_name)
    
    @mock_aws
    def tearDown(self):
        self.mock_aws.stop()

    def test_get_secret(self):
        with mock_aws():
            secret_name = 'test_secret'
            secret_value = 'test_value'

            self.ssm_client.create_secret(
                Name=secret_name,
                SecretString=secret_value
            )

            secret = get_secret(secret_name, self.region_name)

            self.assertEqual(secret, secret_value)

    def test_get_unknown_secret(self):
        with mock_aws():
            secret_name = 'test_secret'

            with self.assertRaises(Exception):
                get_secret(secret_name, self.region_name)
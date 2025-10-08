import boto3
import os
import unittest

from moto import mock_aws
from cmpparis.parameters_utils import *

class TestParameters(unittest.TestCase):
    @mock_aws
    def setUp(self):
        self.mock_aws = mock_aws()
        self.mock_aws.start()

        os.environ['AWS_ACCESS_KEY_ID'] = 'testing' 
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'

        self.ssm = boto3.client('ssm', 'eu-west-3')

    def tearDown(self):
        self.mock_aws.stop()

    def test_get_parameter_with_one_parameter(self):
        with mock_aws():
            self.ssm.put_parameter(
                Name='/test',
                Value='test_value',
                Type='String'
            )

            parameter = get_parameter('test')

            self.assertEqual(parameter, 'test_value')

    def test_get_parameter_with_two_parameters(self):
        with mock_aws():
            self.ssm.put_parameter(
                Name='/test/parameter',
                Value='test_value',
                Type='String'
            )

            parameter = get_parameter('test', 'parameter')

            self.assertEqual(parameter, 'test_value')

    def test_get_parameter_with_one_parameter_not_found(self):
        with mock_aws():
            with self.assertRaises(Exception):
                raise get_parameter('test')

    def test_get_parameter_with_two_parameters_not_found(self):
        with mock_aws():
            with self.assertRaises(Exception):
                raise get_parameter('test', 'parameter')

    def test_get_parameters_path(self):
        with mock_aws():
            self.ssm.put_parameter(
                Name='/test/parameter',
                Value='test_value',
                Type='String'
            )

            self.ssm.put_parameter(
                Name='/test/parameter2',
                Value='test_value2',
                Type='String'
            )

            parameters = get_parameters('/test', True)
            param1 = parameters[0]['Value']
            param2 = parameters[1]['Value']

            self.assertEqual(len(parameters), 2)
            self.assertEqual(param1, 'test_value')
            self.assertEqual(param2, 'test_value2')

    def test_get_parameters_path_not_found(self):
        with mock_aws():
            self.ssm.put_parameter(
                Name='/test2/parameter',
                Value='test_value',
                Type='String'
            )

            with self.assertRaises(Exception):
                raise get_parameters('test')

            with self.assertRaises(Exception):
                raise get_parameters('/test')

            with self.assertRaises(Exception):
                raise get_parameters('test2')

    def test_extract_parameter(self):
        with mock_aws():
            self.ssm.put_parameter(
                Name='/test/parameter',
                Value='test_value',
                Type='String'
            )

            parameters = get_parameters('/test', True)
            parameter = extract_parameter(parameters, 'parameter')
            parameter2 = extract_parameter(parameters, 'parameter2')

            self.assertEqual(parameter, 'test_value')
            self.assertIsNone(parameter2)

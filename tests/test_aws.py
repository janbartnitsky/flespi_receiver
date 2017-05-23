# -*- coding: utf-8 -*-

from context import flespi_receiver

import unittest

api_key = 'your_api_key'
channel_id = 0
timeout = 10
delete_flag = True
start_key = 0


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_read_from_flespi(self):
        receiver = flespi_receiver.flespi_receiver()
        receiver.configure(channel_id, api_key, timeout, delete_flag)

        certdir = '/path/to/certificates/directory/'
        aws_handler = flespi_receiver.aws_iot_handler_class(
            root_ca_path= certdir + "root-CA.crt",
            private_key_path= certdir + "test_thing.private.key",
            certificate_path= certdir + "test_thing.cert.pem",
            endpoint = "ajmu1akwku30p.iot.eu-west-1.amazonaws.com")
        receiver.add_handler(aws_handler)

        receiver.start()


if __name__ == '__main__':
    unittest.main()

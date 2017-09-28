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
        receiver.configure(channel_id, api_key, timeout, delete_flag, start_key)

        stdout_handler1 = flespi_receiver.stdout_handler_class(stdout=1)
        receiver.add_handler(stdout_handler1)

        #wialon_handler = flespi_receiver.wialon_retranslator_handler_class(
        #    host='localhost', port=12374)  # specify listening host:port
        #receiver.add_handler(wialon_handler)

        #certdir = '/home/baja/Downloads/aws/'
        #aws_handler = flespi_receiver.aws_iot_handler_class(
        #    root_ca_path= certdir + "root-CA.crt",
        #    private_key_path= certdir + "test_thing.private.key",
        #    certificate_path= certdir + "test_thing.cert.pem",
        #    endpoint = "ajmu1akwku30p.iot.eu-west-1.amazonaws.com")
        #receiver.add_handler(aws_handler)

        # handler will make POST request to flespi IO storage/abque for every messages bunch from channel
        http_handler = flespi_receiver.http_handler_class(url = 'https://flespi.io/storage/abques/names=test_python_http_handler/messages',
            headers = {'Authorization': 'FlespiToken your_api_key'})

        receiver.add_handler(http_handler)

        receiver.start()


if __name__ == '__main__':
    unittest.main()

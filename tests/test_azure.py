# -*- coding: utf-8 -*-

from context import flespi_receiver

import unittest

api_key = 'gr5jkmFPqhN9MVJ6sCGlkz1xzurPUg0ZxV8F5DllIWiiFSeXiJ7s8WNvg49Z8ZOv'
channel_id = 11
timeout = 10
delete_flag = True
start_key = 0


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_read_from_flespi(self):
        receiver = flespi_receiver.flespi_receiver()
        receiver.configure(channel_id, api_key, timeout, delete_flag)

        receiver.target_url = "http://localhost:9004/gw/channels/" + \
            str(channel_id) + '/messages'
        print(receiver.target_url)

        azure_handler = flespi_receiver.azure_iot_handler_class(
            host_name = 'flespi-test6f927.azure-devices.net',
            shared_access_key_name = 'iothubowner',
            shared_acccess_key = 'sysvGUbu1xUhU5onhftKC+uD3CIBK+gRMLBKumBR+T8=',
            idents_dict_file = "idents.pkl")
        receiver.add_handler(azure_handler)

        receiver.start()


if __name__ == '__main__':
    unittest.main()

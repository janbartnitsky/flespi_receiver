# -*- coding: utf-8 -*-

from context import flespi_receiver

import unittest

api_key = 'your_api_key'
channel_id = 0
timeout = 10
delete_flag = True


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_read_from_flespi(self):
        receiver = flespi_receiver.flespi_receiver()
        receiver.configure(channel_id, api_key, timeout, delete_flag)

        stdout_handler1 = flespi_receiver.stdout_handler_class(stdout=1)
        receiver.add_handler(stdout_handler1)

        wialon_handler = flespi_receiver.wialon_retranslator_handler_class(
            host='localhost', port=12374)  # specify listening host:port
        receiver.add_handler(wialon_handler)

        receiver.start()


if __name__ == '__main__':
    unittest.main()

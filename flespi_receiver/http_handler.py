# -*- coding: utf-8 -*-
from .handler_class import handler_class
import urllib3
import requests
import json
import time

class http_handler_class(handler_class):
    def __init__(self, *args, **kwargs):
        # verify required input parameters
        required_args = ['url']
        for param_name in required_args:
            if param_name not in kwargs:
                print('HTTP handler: missing parameter ' + param_name)
                raise ValueError
        self.url = kwargs['url']
        self.headers = kwargs.get('headers')
        self.timeout = kwargs.get('timeout')
        if self.timeout == None or self.timeout < 1:
            self.timeout = 1
        print(self.timeout)

    def _workout_messages(self, msgs_bunch):
        """ retranslate every messages bunch in HTTP body to url specified """
        if msgs_bunch != []:
            while True:
                r = requests.post(self.url, headers = self.headers, data = json.dumps(msgs_bunch))
                # request success condition below - to end the handler
                if r.status_code == 200:
                    break
                print('http_handler: failed to retranslate messages, try again in ' + str(self.timeout) + ' sec')
                time.sleep(self.timeout)
                # next bunch of messages will not be read until this function ends
                # current bunch of messags will be deleted in next request if delete_flag = True is set

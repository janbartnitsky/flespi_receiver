# -*- coding: utf-8 -*-
import asyncio
import functools
import json
from inspect import signature, iscoroutinefunction
import swagger_client
from swagger_client.rest import ApiException
from swagger_client.apis import messages_api


async def get_msgs_from_channel(future, flespi_recv_obj):
    """Get messages from channel with given id from flespi server"""
    CH_SELECTOR = [flespi_recv_obj.channel_id]
    result = None

    # create request parameters dict and stringify it in json style
    request_data = {'curr_key': flespi_recv_obj.curr_key,
                    'timeout': flespi_recv_obj.timeout, 'delete': flespi_recv_obj.delete_flag}
    json_data = json.dumps(request_data)

    # peparation done: use swagger client to send request
    try:
        flespi_recv_obj.api_instance = swagger_client.MessagesApi()
        result = flespi_recv_obj.api_instance.channels_ch_selector_messages_get(
            CH_SELECTOR, data=json_data)
    except ApiException as e:
        print("Exception calling MessagesApi->channels_ch_selector_messages_get: %s\n" % e)
        future.cancel()
        return
    future.set_result(result)


def create_get_msgs_future(flespi_recv_obj):
    """ Create future: result of api request, and callbac to handle result"""
    # intialize future
    restapi_call_done = asyncio.Future()
    # add future for execution
    asyncio.ensure_future(get_msgs_from_channel(
        restapi_call_done, flespi_recv_obj))
    # register callback on future successful execution
    restapi_call_done.add_done_callback(functools.partial(
        rest_response_callback, restapi_call_done, flespi_recv_obj))


def all_callbacks_done(flespi_recv_obj, future):
    """ when all callbacks done - send next request"""
    if future.result():
        create_get_msgs_future(flespi_recv_obj)


def rest_response_callback(function, flespi_recv_obj, future):
    """ Handle restapi call response"""
    if future.cancelled():
        return
    try:
        response = future.result().to_dict()
    # in case of any error - stop the event loop
    except ApiException as e:
        print("Exception when calling restapi call to flespi.io: %s\n" % e)
        flespi_recv_obj.event_loop.stop()

    # update cur_key for the next request
    if response['next_key'] != None:
        flespi_recv_obj.curr_key = response['next_key']

    # create future for run callbacks
    all_handlers_done = asyncio.Future()
    asyncio.ensure_future(run_callbacks_for_messages(
        all_handlers_done, flespi_recv_obj, response['result']))
    all_handlers_done.add_done_callback(functools.partial(
        all_callbacks_done, flespi_recv_obj))

async def run_callbacks_for_messages(future, flespi_recv_obj, messages_tuple):
    """ Async method to create future waiting for multiple coroutines"""
    all_handlers = [
        handler['function'](messages_tuple, handler['parameters'])
        for handler in flespi_recv_obj.handlers
    ]
    print('waiting for all_handlers to complete')
    completed, pending = await asyncio.wait(all_handlers)
    results = [t.result() for t in completed]
    print('results: {!r}'.format(results))

    future.set_result(True)


class flespi_receiver(object):
    """flespi_receiver: initiate, start and manage receiving messages from flespi gateway"""

    def __init__(self):
        """Initiate swagger api messages client"""
        self.api_instance = swagger_client.MessagesApi()
        # create event loop
        self.event_loop = asyncio.get_event_loop()
        # initiate channel id field
        self.channel_id = 0
        # initiate value of curr_key for get-messages request
        self.curr_key = 0
        # create list for callbacks
        self.handlers = []
        # initate default timeout value (in seconds)
        self.timeout = 5
        # specify if receiver have to delete read messages
        self.delete_flag = False
        print('New flespi_receiver instance created')

    def configure(self, ch_id, api_key, timeout, delete_flag):
        """Store source receiver configuration parameters and auth token"""
        self.channel_id = ch_id
        self.timeout = timeout
        self.delete_flag = delete_flag

        # set up swagger api client authorization
        swagger_client.configuration.api_key[
            'Authorization'] = 'FlespiToken ' + api_key

        print('flespi_receiver instance configured')

    def add_handler(self, func, params):
        """Add handler: pair of workout function and configurational params dict"""
        # validate handler:
        if (signature(func).return_annotation.__name__ == 'bool'  # returns bool
                # has 2 input parameters: msgs_bunch and params
                and list((signature(func).parameters).keys()) == ['msgs_bunch', 'params']
                and iscoroutinefunction(func)):  # must be callable as coroutine
            # store handler (with params) adopting conditions
            handler_inst = dict(function=func, parameters=params)
            self.handlers.append(handler_inst)
            print('handler added', func)
        else:
            print('Invalid handler ', func)
            print('handler has to return bool, have 2 input parameters (\'msgs_bunch\', \'params\') and have to be called as coroutine')

    def start(self):
        """Start event loop of flespi receiver"""
        create_get_msgs_future(self)

        # handlers list can not be empty
        if not self.handlers:
            print('Specify at least one handler to start flespi receiver')
            return

        # start the event loop
        try:
            self.event_loop.run_forever()
        except KeyboardInterrupt as e:
            print("Caught keyboard interrupt. Canceling tasks...")
            self.event_loop.stop()
        finally:
            self.event_loop.close()

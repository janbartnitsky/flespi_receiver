# -*- coding: utf-8 -*-
import asyncio
import functools
import json
import urllib3

from .swagger_api_reduced import get_messages_request, ApiException
from .handler_class import handler_class


async def get_msgs_from_channel(future, flespi_recv_obj):
    """Get messages from channel with given id from flespi server"""
    CH_SELECTOR = [flespi_recv_obj.channel_id]
    result = None

    # create request parameters dict and stringify it in json style
    request_data = {'curr_key': flespi_recv_obj.curr_key,
                    'timeout': flespi_recv_obj.timeout,
                    'delete': flespi_recv_obj.delete_flag,
                    'limit_count': flespi_recv_obj.limit_count,
                    'limit_size': flespi_recv_obj.limit_size}
    json_data = {'data': json.dumps(request_data)}

    # peparation done: use swagger client get messages request to receive data
    try:
        result = get_messages_request(flespi_recv_obj, json_data)
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
        response = future.result()
    # in case of any error - stop the event loop
    except ApiException as e:
        print("Exception when calling restapi call to flespi.io: %s\n" % e)
        flespi_recv_obj.event_loop.stop()

    # parse received response from server
    response = json.loads(response.data)

    # update cur_key for the next request
    if 'next_key' in response:
        flespi_recv_obj.curr_key = response['next_key']
    # check for errors in response if something went wrong
    if 'errors' in response:
        print("Exception when calling restapi call to flespi.io: %s\n" %
              response['errors'])
        flespi_recv_obj.event_loop.stop()

    # create future for run callbacks
    all_handlers_done = asyncio.Future()
    asyncio.ensure_future(run_callbacks_for_messages(
        all_handlers_done, flespi_recv_obj, response['result']))
    all_handlers_done.add_done_callback(functools.partial(
        all_callbacks_done, flespi_recv_obj))

async def run_callbacks_for_messages(future, flespi_recv_obj, messages_tuple):
    """ Async method to create future waiting for multiple coroutines"""
    all_handlers = [
        handler.run_handler(messages_tuple)
        for handler in flespi_recv_obj.handlers
    ]
    completed, pending = await asyncio.wait(all_handlers)
    results = [t.result() for t in completed]
    if False in results:
        for i, res in enumerate(results):
            if res == False:
                print('pricessing failed on handler', all_handlers[i])
                print('curr_key=%d' % flespi_recv_obj.curr_key)
        flespi_recv_obj.event_loop.stop()

    future.set_result(True)


class flespi_receiver(object):
    """flespi_receiver: initiate, start and manage receiving messages from flespi gateway"""

    def __init__(self):
        """Initiate swagger api messages client"""
        self.pool_manager = urllib3.PoolManager()
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
        # specify limits for request GET /messages
        self.limit_size = 8388608 # 8 MB
        self.limit_count = 1000
        print('New flespi_receiver instance created')

    def configure(self, ch_id, api_key, timeout=10, delete_flag=False, start_key=0, limit_size=8388608, limit_count=1000):
        """Store source receiver configuration parameters and auth token"""
        self.channel_id = ch_id
        self.target_url = 'https://flespi.io/gw/channels/' + \
            str(ch_id) + '/messages'
        self.timeout = timeout
        self.delete_flag = delete_flag
        self.curr_key = start_key
        self.auth_header = 'FlespiToken ' + api_key
        self.limit_size = limit_size
        self.limit_count = limit_count

        print('flespi_receiver instance configured')

    def add_handler(self, handler_inst):
        """Add handler: pair of workout function and configurational params dict"""
        # validate handler:
        if (isinstance(handler_inst, handler_class)):
            # store handler adopting conditions
            self.handlers.append(handler_inst)
            print('handler added', handler_inst)
        else:
            print('Invalid handler ', handler_inst)

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

# -*- coding: utf-8 -*-
from .handler_class import handler_class

import iothub_service_client as iot_serv
import iothub_client
import sys
import json
import pickle
import asyncio


class azure_iot_handler_class(handler_class):

    def __init__(self, *args, **kwargs):
        # verify required input parameters
        required_args = ['host_name', 'shared_access_key_name',
                         'shared_acccess_key', 'idents_dict_file']
        for param_name in required_args:
            if param_name not in kwargs:
                print('Microsoft Azure IoT handler: missing parameter ' + param_name)
                raise ValueError

        # create connection string and store host name in the object
        self.host_name = kwargs['host_name']
        hub_conn_string = 'HostName=' + self.host_name + ';SharedAccessKeyName=' + kwargs[
            'shared_access_key_name'] + ';SharedAccessKey=' + kwargs['shared_acccess_key']

        self.idents_file = kwargs['idents_dict_file']
        # initialize dict for active connections to Azure devices
        self.idents_clients = {}

        # configure Azure connection istances
        self.iot_reg_mgr = iot_serv.IoTHubRegistryManager(hub_conn_string)
        self.auth_method = iot_serv.IoTHubRegistryManagerAuthMethod.SHARED_PRIVATE_KEY

        # file ident_device.pkl contains python dict where flespi ident string
        # is a key and corresponding Azure device parameter list is a value
        self.fd = open(self.idents_file, "rwb+")
        print(self.fd)
        try:
            self.idents_keys = pickle.load(self.fd)
        except FileNotFoundError:
            self.idents_keys = {}
            pickle.dump(self.idents_keys, self.fd)
        if not isinstance(self.idents_keys, dict):
            print('Azure IoT handler: wrong format of idents file ' + self.idents_file)
            raise ValueError

        print("Microsoft Azure IoT handler: initialized with %d devices" %
              len(self.idents_keys))

    def __del__(self):
        if 'fd' in self.__dict__:
            self.fd.close()

    def _workout_messages(self, msgs_bunch):
        """ retranslate every message to Amazon AWS IoT platform """

        # events list: Azure SDK has only async pushing to IoT hub
        # before proceeding all the messages must be sent
        send_events = []
        for msg in msgs_bunch:
            print(msg)
            cur_ident = msg['ident']
            # flespi "ident" must be tied to Azure IoT hub device
            if cur_ident not in self.idents_keys.keys():
                # create new device on Azure IoT hub
                try:
                    new_dev = self.iot_reg_mgr.create_device(
                        cur_ident, "", "", self.auth_method)
                except IoTHubError as iothub_error:
                    print("Microsoft Azure IoT handler: failed to create a device. error {0}".format(
                        iothub_error))
                    return False
                # remember new device detailes in handler and on disk
                self.idents_keys[cur_ident] = new_dev.primaryKey
                pickle.dump(self.idents_keys, self.fd)

            # now there is a key for given ident to connect to Azure hub
            # check current device is already connected to Azure hub
            if cur_ident not in self.idents_clients.keys():
                conn_string = 'HostName=' + self.host_name + ';DeviceId=' + \
                    cur_ident + ';SharedAccessKey=' + \
                    self.idents_keys[cur_ident]
                self.idents_clients[cur_ident] = iothub_client.IoTHubClient(
                    conn_string, iothub_client.IoTHubTransportProvider.MQTT)

            # create a list of sending coroutines
            send_events.append(self.idents_clients[
                               cur_ident].send_event_async("{\"DeviceId\":\"flespi\", \"Temperature\":50, \"Humidity\":50, \"ExternalTemperature\":55}"))#json.dumps(msg)))

        # send_events - list of sending operations to be parformed
        completed, pending = asyncio.wait(send_events)
        results = [t.result() for t in completed]
        print(results)
        for client in self.idents_clietns:
            if client.get_send_status() == False:
                return False

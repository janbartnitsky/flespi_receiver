# -*- coding: utf-8 -*-
from .handler_class import handler_class
# A copy of the License is located at http://aws.amazon.com/apache2.0
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json

class aws_iot_handler_class(handler_class):

    def __init__(self, *args, **kwargs):
        # verify required input parameters
        required_args = ['root_ca_path', 'private_key_path',
                         'certificate_path', 'endpoint']
        for param_name in required_args:
            if param_name not in kwargs:
                print('Amazon AWS IoT handler: missing parameter ' + param_name)
                raise ValueError

        # init Amazon AWS IoT client
        self.aws_iot_mqtt_client = AWSIoTMQTTClient("flespi_reseiver")
        self.aws_iot_mqtt_client.configureEndpoint(kwargs['endpoint'], 8883)
        self.aws_iot_mqtt_client.configureCredentials(kwargs['root_ca_path'], kwargs[
            'private_key_path'], kwargs['certificate_path'])

        # connection configuration taken from demo samples basicPubSub.py
        self.aws_iot_mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.aws_iot_mqtt_client.configureOfflinePublishQueueing(-1)
        self.aws_iot_mqtt_client.configureDrainingFrequency(2)
        self.aws_iot_mqtt_client.configureConnectDisconnectTimeout(10)
        self.aws_iot_mqtt_client.configureMQTTOperationTimeout(5)

        self.aws_iot_mqtt_client.connect()

    def __del__(self):
        if 'aws_iot_mqtt_client' in self.__dict__:
            self.aws_iot_mqtt_client.disconnect()

    def _workout_messages(self, msgs_bunch):
        """ retranslate every message to Amazon AWS IoT platform """
        ret = True
        for msg in msgs_bunch:
            ret = self.aws_iot_mqtt_client.publish(msg["ident"], json.dumps(msg), 1)
            if ret == False:
                break
        return ret


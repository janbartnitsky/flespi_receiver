Flespi Receiver
===============

This library is used to get messages from flespi gateway channel and handle it via specified approach.

Getting started:
This library is written using ayncio library for Python 3.5 version. To run the example script do:

1. make init: 
initialize local virtual environment with python3.5

2. make build: 
builds the project of flespi_reciever and swagger_client modules

3. make test: 
runs test/test.py script

Basic usage example (see tests/test.py):
----------------------------------------

1. import module

``import flespi_receiver``

2. initiate flespi_receiver object

``receiver = flespi_receiver.flespi_receiver()``

3. configure object with:

- id of a channel where to read messages

- Token key (without FlespiToken keyword) to provide access to the channel

- timeout - request will wait for new messages for the specified amount of seconds

- delete_flag - point True if successfuly handled messags may be removed

- start_key - point curr_key pointing to the beginning of messages bunch to be read

``api_key = 'your_api_key'``

``channel_id = 0``

``timeout = 10``

``delete_flag = True``

``start_key = 0``

``receiver.configure(channel_id, api_key, timeout, delete_flag, start_key)``

4. create handlers and add it to the receiver object

``stdout_handler1 = flespi_receiver.stdout_handler_class(stdout=1)``

``receiver.add_handler(stdout_handler1)``

5. start the receiving and peocessing process

``receiver.start()``

Concept:

    receiver will generate GET /channels/channel_id/messages request returning bunch of messages from the channel
    
    for each bunch of messages every handler will be used in an asynchronos way.
    
    When all handlers return - next GET /messages request will be sent. So if one of the handlers will stuck - no new GET /messages requests will besent.
    
Available handlers:

| Name          | Used for      | Required parameters |
| ------------- | ------------- | ------------------- |
| stdout | print received messages to the console | - |
| wialon | send received messages to specified IP:port using wialon retranslator protocol | host, port |
| aws_iot | send received messages to Amazon AWS IoT hub | root_ca_path, private_key_path, certificate_path, endpoint |
| http | send POST http request to specified URL with specified headers with messages list as a HTTP data parameter | URL |



# -*- coding: utf-8 -*-
import asyncio
from math import floor
from .handler_class import handler_class
import struct
import io
import socket


def enc_msgs_to_wialon_retr_fmt(msgs_bunch):
    """ iterate over messages and encode message fields """
    encoded_buf = io.BytesIO()  # output buffer

    for msg in msgs_bunch:
        # ident and timestamp are mandatory parameters in flespi message
        ident_string = bytes(msg['ident'] + '\x00', 'utf-8')
        head_chunk = struct.pack("!%ds i 4s" % (len(ident_string)), ident_string,
                                 int(floor(msg["timestamp"])), b'\x00\x00\x00\x01')

        chunks_list = []
        chunks_list.append(head_chunk)
        single_msg_size = len(head_chunk)
        for param_key, param_value in msg.items():
            if param_key == ("ident" or "timestamp"):
                continue  # these values have been already added in block head
            # init blocksize: 1(hidden_flag)+1(type)+len(param_key)+1(endline)
            block_size_init = 3 + len(param_key)
            # init struct format: 0x0BBB, blocksize, flag+type
            fmt = '! 2s I 2s'
            # initialize and start single value encoding
            param_chunk = None
            # TODO: check if there is need in "posinfo" binary block
            if isinstance(param_value, str):
                fmt += str(len(param_value) + len(param_key) + 1) + 's'
                param_chunk = struct.pack(fmt, b'\x0B\xBB', len(param_value) + block_size_init,
                                          b'\x00\x01', bytes(param_key + '\0' + param_value, 'utf-8'))
            elif isinstance(param_value, float):
                fmt += str(len(param_key) + 1) + 's'
                param_chunk = struct.pack(fmt, b'\x0B\xBB', 8 + block_size_init,
                                          b'\x00\x04', bytes(param_key + '\0', 'utf-8')) + struct.pack('d', param_value)
            elif isinstance(param_value, int):
                # as in Python3 there is no long() type - check it manually
                if param_value.bit_length() <= 32:
                    fmt += str(len(param_key) + 1) + 's i'
                    param_chunk = struct.pack(fmt, b'\x0B\xBB', 4 + block_size_init,
                                              b'\x00\x03', bytes(param_key + '\0', 'utf-8'), param_value)
                else:
                    fmt += str(len(param_key) + 1) + 's q'
                    param_chunk = struct.pack(fmt, b'\x0B\xBB', 8 + block_size_init,
                                              b'\x00\x03', bytes(param_key + '\0', 'utf-8'), param_value)

            # encoding's done, store result in a chunks list
            if param_chunk:
                chunks_list.append(param_chunk)
                single_msg_size += len(param_chunk)

        # parameters are writter to chunks_list, we have size of a single message
        # add packet size to out buffer
        encoded_buf.write(struct.pack("I", single_msg_size))
        # and store all the encoded data to output buffer
        for param_chunk in chunks_list:
            encoded_buf.write(param_chunk)

    return encoded_buf.getvalue()


class wialon_retranslator_handler_class(handler_class):

    def __init__(self, config):
        """ assert that config is a dict with host and port fields """
        if 'host' not in config or 'port' not in config:
            print('wialon retranslator handler must have host and port in config dict')
            return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # establish TCP connection to host port from config
        self.sock.connect((config['host'], config['port']))

    def __del__(self):
        self.sock.close()

    async def run_handler(self, msgs_bunch) -> bool:
        """ encode every message with wialon_retranslator protocol """
        encoded_buffer = enc_msgs_to_wialon_retr_fmt(msgs_bunch)
        # print(binascii.hexlify(bytearray(encoded_buffer)))
        # send encoded data to established at init connection
        self.sock.sendall(encoded_buffer)
        # server returns '\x11' code on every message which we ignore
        """recv_codes = self.sock.recv(len(msgs_bunch))"""
        return True

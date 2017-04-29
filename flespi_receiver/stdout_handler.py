# -*- coding: utf-8 -*-
from .handler_class import handler_class


class stdout_handler_class(handler_class):

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    def _workout_messages(self, msgs_bunch):
        print(msgs_bunch)
        return True

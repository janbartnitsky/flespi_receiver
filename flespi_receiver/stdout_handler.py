# -*- coding: utf-8 -*-
import asyncio
from .handler_class import handler_class


class stdout_handler_class(handler_class):

    def __init__(self, config):
        # assert that config is a dict
        self.config = config

    async def run_handler(self, msgs_bunch) -> bool:
        print(self.config, '\n', msgs_bunch)
        return True

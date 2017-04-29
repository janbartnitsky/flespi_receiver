# -*- coding: utf-8 -*-
import asyncio
from abc import ABCMeta, abstractmethod


class handler_class(metaclass=ABCMeta):
    """handler_class: consists of single handler method to workout messages"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def run_handler(self, msgs_bunch) -> bool:
        """ handler to workout the received messages """
        try:
            handler_ret = self._workout_messages(msgs_bunch)
        except:
            return False

        return handler_ret

    @abstractmethod
    def _workout_messages(self, msgs_bunch) -> bool:
        raise NotImplementedError

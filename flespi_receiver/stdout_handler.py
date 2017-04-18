# -*- coding: utf-8 -*-
import asyncio

async def write_to_stdout(msgs_bunch, params) -> bool:
    """ file handler to append the received messages bunch to a file """
    print(params, '\n', msgs_bunch)
    return True

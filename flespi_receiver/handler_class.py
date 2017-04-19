# -*- coding: utf-8 -*-
import asyncio
from abc import ABCMeta, abstractmethod


class handler_class(metaclass=ABCMeta):
	"""handler_class: consists of single handler method to workout messages"""
	config = {}

	@abstractmethod
	def __init__(self, config):
		"""Initiate handler instance"""
		pass

	@abstractmethod
	async def run_handler(self, msgs_bunch) -> bool:
		""" file handler to append the received messages bunch to a file """
		pass

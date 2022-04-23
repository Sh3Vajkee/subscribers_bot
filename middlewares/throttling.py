from cachetools import TTLCache
import asyncio
from math import inf

from aiogram import Dispatcher, types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


caches = {
    "default": TTLCache(maxsize=inf, ttl=0),
}


def rate_limit(key="default"):

    def decorator(func):
        setattr(func, 'throttling_key', key)
        return func
    return decorator


class ThrottlingMiddleware(BaseMiddleware):

    def __init__(self):
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):

        handler = current_handler.get()

        throttling_key = getattr(handler, 'throttling_key', None)

        if throttling_key and throttling_key in caches:
            if not caches[throttling_key].get(message.chat.id):
                caches[throttling_key][message.chat.id] = True
                return
            else:
                raise CancelHandler()

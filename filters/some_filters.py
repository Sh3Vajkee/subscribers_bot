from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsAdmin(BoundFilter):
    key = 'is_admin'

    async def check(self, message: types.Message):
        admins = [746461090]
        return message.from_user.id in admins

import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter
from db.models import SubBuyers


async def user_joined(m: types.Message):
    db_ssn = m.bot.get("db")

    async with db_ssn() as ssn:

        for user in m.new_chat_members:
            await ssn.merge(SubBuyers(user_id=user.id))
            logging.info(f"UserID:{user.id} joined!")
    await ssn.commit()


async def user_left(m: types.Message):
    db_ssn = m.bot.get("db")

    async with db_ssn() as ssn:
        usr: SubBuyers = await ssn.get(SubBuyers, m.left_chat_member.id)
        usr.status = "left"
        await ssn.commit()

        logging.info(f"UserID:{m.left_chat_member.id} left!")


def members_handlers(dp: Dispatcher):
    dp.register_message_handler(
        user_joined,
        ChatTypeFilter(
            chat_type=[
                types.ChatType.GROUP,
                types.ChatType.SUPERGROUP,
            ]
        ),
        content_types=types.ContentTypes.NEW_CHAT_MEMBERS
    )
    dp.register_message_handler(
        user_left,
        ChatTypeFilter(
            chat_type=[
                types.ChatType.GROUP,
                types.ChatType.SUPERGROUP,
            ]
        ),
        content_types=types.ContentTypes.LEFT_CHAT_MEMBER
    )

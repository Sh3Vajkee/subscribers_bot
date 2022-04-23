import asyncio
import logging
from datetime import date

from aiogram import Dispatcher
from db.models import SubBuyers
from keyboars import get_buy_kb
from sqlalchemy import select


async def check_balance(dp: Dispatcher):
    db_ssn = dp.bot.get("db")

    async with db_ssn() as ssn:
        query_users = await ssn.execute(select(SubBuyers).filter(SubBuyers.status == "member"))
        usrs = query_users.scalars()

        positive_balance_query = await ssn.execute(
            select(SubBuyers).filter(SubBuyers.balance >
                                     0).filter(SubBuyers.status == "left")
        )
        positive_balance = positive_balance_query.scalars()

        count_kicked = 0
        for user in usrs:

            if user.balance == 0:
                await dp.bot.unban_chat_member(-1001655542688, user.user_id)
                await dp.bot.send_message(user.user_id, 'Вы были кикнуты из группы, так как не продлили подписку!')
                logging.info(
                    f"UserID:{user.user_id} kicked because not enough balance({user.balance})")
                count_kicked = + 1

            elif user.balance == 1:
                await dp.bot.send_message(user.user_id, 'Продлите подписку!', reply_markup=get_buy_kb())

                user.balance -= 1

            else:
                user.balance -= 1

            await asyncio.sleep(0.1)

        for user in positive_balance:
            user.balance -= 1

        await ssn.commit()

    logging.info(f"Check over! {count_kicked} users were kicked!")

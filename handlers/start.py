import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode, hlink
from db.models import Subscribers
from keyboars import get_buy_kb, pay_kb

# from utils.qiwi import NoPaymentFound, NotEnoughMoney, Payment, qiwi_wallet


async def start_cmd(m: types.Message):
    await m.answer('Чтобы получить доступ в группу необходимо оплатить подписку за 100RUB', reply_markup=get_buy_kb())


async def buy_sub(c: types.CallbackQuery, state: FSMContext):
    await c.answer(cache_time=60)
    await c.message.delete_reply_markup()

    amount = 100

    await c.message.answer(f"К оплате {amount} RUB", reply_markup=pay_kb)

    # payment = Payment(amount=amount)
    # payment.create()

    # await c.message.answer(
    #     "\n".join(
    #         [
    #             f"К оплате {amount} RUB",
    #             "",
    #             hlink(qiwi_wallet, url=payment.link),
    #             "Указать ID платежа:",
    #             hcode(payment.id)
    #         ]
    #     ),
    #     reply_markup=pay_kb
    # )
    await state.set_state("qiwi")
    # await state.set_data(payment=payment)


async def cancel_payment(c: types.CallbackQuery, state: FSMContext):
    await c.message.edit_text("Платеж отменен!")
    await state.finish()


async def accept_payment(c: types.CallbackQuery, state: FSMContext):
    # data = await state.get_data()
    # payment: Payment = data.get("payment")

    # try:
    #     payment.check_payment()
    # except NoPaymentFound:
    #     await c.message.answer('Платеж не найдет')
    #     return
    # except NotEnoughMoney:
    #     await c.message.answer('Недостаточно средств')
    #     return
    # else:
    #     await c.message.answer('Успешно оплачено')
    # await c.message.delete_reply_markup()
    # await state.finish()
    db_session = c.bot.get("db")

    async with db_session() as ssn:
        await ssn.merge(
            Subscribers(
                user_id=c.from_user.id,
                is_paid=True
            )
        )
        await ssn.commit()

    await c.message.delete_reply_markup()
    await c.message.answer('Теперь вы можете <a href="https://t.me/+8I97k55EtEEzNzMy">подать заявку</a> в группу!')
    await state.finish()


async def check_sub(user_id, group_id, bot: Bot):
    asyncio.sleep(15)
    await bot.send_message('Вам необходимо продлить подписку на группу', reply_markup=get_buy_kb())

    asyncio.sleep(15)

    db_session = bot.get("db")
    async with db_session() as ssn:
        usr: Subscribers = await ssn.get(Subscribers, user_id)

    if usr.is_paid is True:
        await bot.send_message(user_id, 'Ваша подписка продлена!')
        asyncio.create_task(check_sub(user_id, group_id, bot))

    else:
        await bot.send_message(user_id, 'Вы не продлили подписку на группу!')
        await bot.unban_chat_member(group_id, user_id)


async def join_request(u: types.ChatJoinRequest):
    db_session = u.bot.get("db")

    uid = u.from_user.id
    gid = u.chat.id

    async with db_session() as ssn:
        usr: Subscribers = await ssn.get(Subscribers, uid)

    if usr:

        if usr.is_paid is True:
            await u.approve()

            async with db_session() as ssn:
                usr: Subscribers = await ssn.get(Subscribers, uid)
                usr.is_paid = False
                await ssn.commit()

            await u.bot.send_message(uid, 'Добро пожаловать в группу!')

            asyncio.create_task(check_sub(uid, gid, u.bot))
    else:
        await u.decline()

        await u.bot.send_message(uid, 'Для вступления в группу необходимо оплатить подписку \n/start')


def start_handlers(dp: Dispatcher):
    dp.register_chat_join_request_handler(join_request)
    dp.register_message_handler(start_cmd, commands='start')
    dp.register_callback_query_handler(buy_sub, text='buy_sub')
    dp.register_callback_query_handler(
        cancel_payment, text='cancel', state="qiwi")
    dp.register_callback_query_handler(
        accept_payment, text='done', state="qiwi")

import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, Text
from db.models import SubBuyers
from keyboars import get_buy_kb, pay_kb, start_kb
from middlewares.throttling import rate_limit


@rate_limit("default")
async def start_cmd(m: types.Message):
    await m.answer(
        "Вы можете проверить баланс, пополнить баланс или подать заявку в группу",
        reply_markup=start_kb
    )


@rate_limit("default")
async def balance_cmd(m: types.Message):
    db_ssn = m.bot.get("db")

    async with db_ssn() as ssn:
        usr: SubBuyers = await ssn.get(SubBuyers, m.from_user.id)

    if usr:
        await m.answer(f"Ваш баланс <b>{usr.balance} RUB</b>")
    else:
        await m.answer("Ваш баланс <b>0 RUB</b>")


@rate_limit("default")
async def sub_cmd(m: types.Message):
    await m.answer(
        'Чтобы получить доступ в группу необходимо пополнить баланс.'
        'Затем набрать команду <b>/invite</b>.',
        reply_markup=get_buy_kb()
    )


async def buy_cmd(c: types.CallbackQuery, state: FSMContext):

    await c.answer(cache_time=60)
    await c.message.delete_reply_markup()

    amount = 5
    db_ssn = c.bot.get("db")

    async with db_ssn() as ssn:
        await ssn.merge(SubBuyers(user_id=c.from_user.id))
        await ssn.commit()

    await c.message.answer(f"К оплате {amount} RUB", reply_markup=pay_kb)
    await state.set_state("buying")


async def accept_sub(c: types.CallbackQuery, state: FSMContext):
    db_ssn = c.bot.get("db")

    async with db_ssn() as ssn:
        buyer: SubBuyers = await ssn.get(SubBuyers, c.from_user.id)
        buyer.balance += 5
        await ssn.commit()

    await c.message.delete_reply_markup()
    await state.finish()


async def cancel_sub(c: types.CallbackQuery, state: FSMContext):
    await c.message.edit_text("Платеж отменен!")
    await state.finish()


@rate_limit("default")
async def invite_cmd(m: types.Message):
    await m.answer('<a href="https://t.me/+8I97k55EtEEzNzMy">Подать заявку</a> в группу!')


async def chat_join_req(u: types.ChatJoinRequest):
    uid = u.from_user.id
    db_ssn = u.bot.get("db")

    async with db_ssn() as ssn:
        usr: SubBuyers = await ssn.get(SubBuyers, uid)

        if usr:

            if usr.balance > 0:
                await u.approve()
                await u.bot.send_message(uid, 'Добро пожаловать в группу!')
                logging.info(
                    f"UserID: {uid} with balance: {usr.balance} approved!")
                usr.status = "member"

            else:
                await u.decline()
                await u.bot.send_message(uid, 'Вы не оплатили подписку!')
                logging.info(
                    f"UserID: {uid} with balance: {usr.balance} declined!")

        else:
            await u.decline()
            await u.bot.send_message(uid, 'Вы не оплатили подписку!\n/sub', reply_markup=get_buy_kb())
            logging.info(f"UserID: {uid} not found in DataBase!")

        await ssn.commit()


def subs_handlers(dp: Dispatcher):
    dp.register_chat_join_request_handler(chat_join_req)
    dp.register_message_handler(start_cmd, ChatTypeFilter(
        chat_type=[types.ChatType.PRIVATE]), commands='start')
    dp.register_message_handler(balance_cmd, ChatTypeFilter(
        chat_type=[types.ChatType.PRIVATE]), Text(equals="💵Баланс"))
    dp.register_message_handler(balance_cmd, ChatTypeFilter(
        chat_type=[types.ChatType.PRIVATE]), commands="balance")
    dp.register_message_handler(sub_cmd, ChatTypeFilter(
        chat_type=[types.ChatType.PRIVATE]), Text(equals="💳Пополнить счет"))
    dp.register_message_handler(sub_cmd, ChatTypeFilter(
        chat_type=[types.ChatType.PRIVATE]), commands='sub')
    dp.register_message_handler(invite_cmd, ChatTypeFilter(
        chat_type=[types.ChatType.PRIVATE]), Text(equals="🧾Подать заявку"))
    dp.register_message_handler(invite_cmd, ChatTypeFilter(
        chat_type=[types.ChatType.PRIVATE]), commands='invite')
    dp.register_callback_query_handler(buy_cmd, text="buy_sub")
    dp.register_callback_query_handler(accept_sub, text="done", state="buying")
    dp.register_callback_query_handler(
        cancel_sub, text="cancel", state="buying")

from aiogram import types


def get_buy_kb():
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(
                text='Оплатить', callback_data='buy_sub')]
        ]
    )

    return keyboard


pay_kb = types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            types.InlineKeyboardButton(text='Оплатил', callback_data='done')
        ],
        [
            types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        ]
    ]
)

start_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="💵Баланс")
        ],
        [
            types.KeyboardButton(text="💳Пополнить счет")
        ],
        [
            types.KeyboardButton(text="🧾Подать заявку")
        ],
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)

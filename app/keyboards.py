from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)


# Создание inline клавиатуры с нужным функционалом
multifunc_kb = InlineKeyboardMarkup(row_width=1)

button_weather = InlineKeyboardButton(text='Узнать погоду',
                                      callback_data='погода')
button_currency_convert = InlineKeyboardButton(text='Конвертировать валюту',
                                               callback_data='валюта')
button_send_animal = InlineKeyboardButton(text='Милое животное',
                                          callback_data='животное')
button_make_polls = InlineKeyboardButton(text='Создать опрос',
                                         callback_data='опрос')
button_cancel = InlineKeyboardButton(text='Отмена',
                                     callback_data='отмена')

(multifunc_kb.add(button_weather).add(button_currency_convert)
 .add(button_send_animal).add(button_make_polls))

multifunc_kb.add(button_cancel)

# Создание основной клавиатуры
button_funcs = KeyboardButton('Функционал')
button_help = KeyboardButton('Помощь')

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

menu_keyboard.add(button_funcs).insert(button_help)

# клавиатура повторить попытку/отмена
else_or_cancel_kb = InlineKeyboardMarkup()
repeat_button = InlineKeyboardButton(text='Повторить',
                                     callback_data='повторить')
else_or_cancel_kb.add(button_cancel).add(repeat_button)

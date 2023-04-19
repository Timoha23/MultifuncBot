# Данный файл предназначен для регистрации обработчиков

from aiogram import Dispatcher

from handlers.main_handlers import start_command, get_funcs, get_weather, callback_type, States, else_or_cancel, get_currency_conversion, make_poll


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(get_funcs, text='Функционал')
    dp.register_message_handler(get_weather, state=States.weather)
    dp.register_message_handler(get_currency_conversion, state=States.currency_conversion)
    dp.register_message_handler(make_poll, state=States.make_poll)
    dp.register_callback_query_handler(callback_type, state=States.callback_type)
    dp.register_callback_query_handler(else_or_cancel, state=States.else_or_cancel)

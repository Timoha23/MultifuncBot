# Файл с обработчиками
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BadRequest, ChatNotFound

from core.poll_validate import poll_validator
from create_bot import bot
from external_api import animal_api, currency_conversion_api, weather_api
from keyboards import else_or_cancel_kb, menu_keyboard, multifunc_kb


class States(StatesGroup):
    """
    Создаем состояния
    """

    callback_type = State()
    weather = State()
    currency_conversion = State()
    make_poll = State()
    else_or_cancel = State()


async def start_command(message: types.Message):
    """
    Обработка команды /start
    """

    await message.answer(f'Привет, {message.from_user.first_name}.',
                         reply_markup=menu_keyboard)


async def funcs(message: types.Message):
    """
    Обработчик показывающий функционал бота
    """

    await message.answer('Выбери что тебя интересует',
                         reply_markup=multifunc_kb)
    await States.callback_type.set()


async def callback_type(callback_query: types.CallbackQuery,
                        state: FSMContext):
    """
    Обработчик колбэка при выборе функции
    """

    async with state.proxy() as data:
        data['type_callback'] = callback_query.data
    if data['type_callback'] == 'погода':
        await callback_query.message.answer('Напишите город, в котором хотите'
                                            ' узнать погоду:')
        await States.weather.set()
    elif data['type_callback'] == 'валюта':
        await callback_query.message.answer('Напишите валюту и сумму в '
                                            'формате: FROM:TO:AMOUNT'
                                            ' (Пример: USD:EUR:30)')
        await States.currency_conversion.set()
    elif data['type_callback'] == 'животное':
        await animal_image(callback_query.message)
    elif data['type_callback'] == 'опрос':
        await callback_query.message.answer(
            'Создайте ваш опрос.\nОбразец: *{\n"question": "заголовок опроса",'
            '\n"answers": ["вариант1", "вариант2", ...],\n"chat_id": ID чата'
            ' куда отправить опрос,\n"is_anon": анонимный(1)/неанонимный(0) '
            'опрос\n}*\nПример: *{\n"question": "Любите ли вы лабрадоров?",\n'
            '"answers": ["Да", "Конечно"],\n"chat_id": 1234567890,'
            '\n"is_anon": 1\n}*', parse_mode='Markdown'
        )
        await States.make_poll.set()
    else:
        await state.finish()
    await callback_query.message.delete()


async def weather(message: types.Message, state: FSMContext):
    """
    Обработчик погоды
    """

    weather = await weather_api.get_weather(message.text)

    if weather['cod'] == 200:
        city = weather['name']
        temp = weather['main']['temp']
        description = weather['weather'][0]['description']
        feels_like = weather['main']['feels_like']
        temp_min = weather['main']['temp_min']
        temp_max = weather['main']['temp_max']
        wind_speed = weather['wind']['speed']
        weather_message = (f'Погода в городе: {city}\n'
                           f'Погодные условия: {description}\n'
                           f'Температура: {temp}°C\n'
                           f'Ощущается: {feels_like}°C\n'
                           f'Минимальная температура: {temp_min}°C\n'
                           f'Максимальная температура: {temp_max}°C\n'
                           f'Скорость ветра: {wind_speed} м/с'
                           )
        await message.answer(weather_message)
        await state.finish()
    elif weather['cod'] == 'server_error':
        await message.reply('К сожалению, на данный момент сервер не '
                            'отвечает :(')
        await state.finish()
    elif weather['cod'] == '404':
        await message.reply('К сожалению, такой город не найден.',
                            reply_markup=else_or_cancel_kb)
        await States.else_or_cancel.set()


async def currency_conversion(message: types.Message, state: FSMContext):
    """
    Обработчик конвертации валют
    """

    data = {}
    text = message.text.split(':')
    if len(text) != 3:
        await message.reply('Данные введены в неверном формате.',
                            reply_markup=else_or_cancel_kb)
        await States.else_or_cancel.set()
    else:
        data.update({'from': text[0], 'to': text[1], 'amount': text[2]})
        wait_message = await message.answer('Ожидаем ответ от сервера...')
        conversion = await currency_conversion_api.get_conversion(data)
        await wait_message.delete()
        if conversion.get('error'):
            if conversion['error'] == 'server_error':
                await message.reply('К сожалению, на данный момент сервер не'
                                    ' отвечает :(')
                await state.finish()
                return
            elif conversion['error']['code'] == 401:
                await message.reply(
                    f'Введена некоректная валюта FROM ({text[0]}).',
                    reply_markup=else_or_cancel_kb
                )
            elif conversion['error']['code'] == 402:
                await message.reply(
                    f'Введена некоректная валюта TO ({text[1]}).',
                    reply_markup=else_or_cancel_kb
                )
            elif conversion['error']['code'] == 403:
                await message.answer(
                    f'Введено некоректное число AMOUNT ({text[2]}).',
                    reply_markup=else_or_cancel_kb
                )
            await States.else_or_cancel.set()
        elif conversion.get('success'):
            result = conversion['result']
            date = datetime.fromtimestamp(conversion['info']['timestamp'])
            to_currency = data['to'].upper()
            from_currency = data['from'].upper()
            amount = data['amount']
            conversion_message = (
                f'Конвертация прошла упешно!\n'
                f'Валюты: {from_currency} -> {to_currency}\n'
                f'Количество монет: {amount} {from_currency}\n'
                f'Результат: {result:.2f} {to_currency}\n'
                f'Дата конвертации: {date}'
            )
            await message.answer(conversion_message)
            await state.finish()


async def animal_image(message: types.Message):
    """
    Обработчик отправки фото животного
    """

    image = await animal_api.get_animal_image()
    try:
        await message.answer_photo(image, reply_markup=else_or_cancel_kb)
    except BadRequest:
        await message.answer('Ошибка на стороне API. Попробуйте еще раз',
                             reply_markup=else_or_cancel_kb)
    await States.else_or_cancel.set()


async def make_poll(message: types.Message, state: FSMContext):
    """
    Обработчик создания опроса
    """

    data = await poll_validator(message.text)
    if data.get('error'):
        await message.answer(data.get('description'),
                             reply_markup=else_or_cancel_kb)
        await States.else_or_cancel.set()
    else:
        # проверяем является ли юзер админом группы, если нет,
        # то отклоняем создание опроса
        admins = await bot.get_chat_administrators(chat_id=data['chat_id'])
        is_admin = False
        for admin in admins:
            if message.from_user.id == admin['user']['id']:
                is_admin = True
        if is_admin is False:
            await message.answer(
                'Вы не являетесь администратором данной группы. '
                'Ваш запрос на создание опроса отклонен.',
                reply_markup=else_or_cancel_kb
            )
            await States.else_or_cancel.set()
            return
        try:
            await bot.send_poll(
                chat_id=data['chat_id'],
                question=data['question'],
                options=data['answers'],
                is_anonymous=data['is_anon']
            )
            await message.answer('Опрос успешно отправлен!')
            await state.finish()
        except ChatNotFound:
            await message.answer('Чат не найден. Убедитесь что ввели верный'
                                 ' и чат, и бот добавлен в ваш чат.',
                                 reply_markup=else_or_cancel_kb)
            await States.else_or_cancel.set()
        except BadRequest:
            await message.answer('Неанонимные опросы нельзя отправлять в '
                                 'чаты канала',
                                 reply_markup=else_or_cancel_kb)
            await States.else_or_cancel.set()


async def else_or_cancel(callback_query: types.CallbackQuery,
                         state: FSMContext):
    """
    Обработчик колбэка с отмена/повторить
    """

    async with state.proxy() as data:
        data['else_or_cancel'] = callback_query.data
    if data['else_or_cancel'] == 'отмена':
        await state.finish()
        # на данном этапе мы не удаляем целиком сообщение (картинку),
        # а только клавиатуру
        if data['type_callback'] == 'животное':
            await callback_query.message.edit_reply_markup(reply_markup=None)
            return
    elif data['else_or_cancel'] == 'повторить':
        if data['type_callback'] == 'погода':
            await States.weather.set()
            await callback_query.message.answer('Введите название города еще '
                                                'раз:')
        elif data['type_callback'] == 'валюта':
            await States.currency_conversion.set()
            await callback_query.message.answer('Введите данные для'
                                                ' конвертации еще раз:')
        elif data['type_callback'] == 'животное':
            await callback_query.message.edit_reply_markup(reply_markup=None)
            await animal_image(callback_query.message)
            return
        elif data['type_callback'] == 'опрос':
            await States.make_poll.set()
            await callback_query.message.answer('Введите данные'
                                                ' для опроса еще раз:')
    await callback_query.message.delete()


async def unknown(message: types.Message):
    """
    Обработка неизвестных команд/сообщений
    """

    await message.reply('Неизвестная команда')

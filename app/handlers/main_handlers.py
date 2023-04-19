# Файл с обрабоитчиками

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import ChatNotFound, BadRequest

from create_bot import bot
from core.poll_validate import poll_validator
from keyboards import multifunc_kb, menu_keyboard, else_or_cancel_kb
from external_api import weather_api, currency_conversion_api, animal_api


class States(StatesGroup):
    callback_type = State()
    weather = State()
    currency_conversion = State()
    animal_image = State()
    make_poll = State()
    else_or_cancel = State()


async def start_command(message: types.Message):
    """
    Обработка команды /start
    """

    await message.answer(f"Привет, {message.from_user.username}.", reply_markup=menu_keyboard)


async def get_funcs(message: types.Message):
    """
    Обработчик команды /funcs
    """
    await message.answer("Выбери что тебя интересует",
                         reply_markup=multifunc_kb)
    await States.callback_type.set()


async def callback_type(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик колбэка
    """

    async with state.proxy() as data:
        data["type_callback"] = callback_query.data
    if data["type_callback"] == "погода":
        await callback_query.message.answer("Напишите город, в котором хотите узнать погоду:")
        await States.weather.set()
        print('Погода')
    elif data["type_callback"] == "валюта":
        await callback_query.message.answer("Напишите валюту и сумму в формате: TO:FROM:AMOUNT (Пример: USD:EUR:30)")
        await States.currency_conversion.set()
        print('Валюта')
    elif data["type_callback"] == "животное":
        await get_animal_image(callback_query.message)
    elif data["type_callback"] == "опрос":
        await callback_query.message.answer(
            'Создайте ваш опрос.\nОбразец: *{\n"question": "заголовок опроса",\n'
            '"answers": ["вариант1", "вариант2", ...],\n"chat_ID": ID чата куда '
            'отправить опрос,\n"is_anon": анонимный(1)/неанонимный(0) '
            'опрос\n}*\nПример: *{\n"question": "Любите ли вы лабрадоров?",\n'
            '"answers": ["Да", "Конечно"],\n"chat_id": 1234567890,'
            '\n"is_anon": 0\n}*', parse_mode='Markdown'
        )
        await States.make_poll.set()
    else:
        await state.finish()
    await callback_query.message.delete()


async def get_weather(message: types.Message, state: FSMContext):
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
        await message.reply('К сожалению, на данный момент сервер не отвечает :(')
        await state.finish()
    elif weather['cod'] == '404':
        await message.reply('К сожалению, такой город не найден.', reply_markup=else_or_cancel_kb)
        await States.else_or_cancel.set()


async def get_currency_conversion(message: types.Message, state: FSMContext):
    """
    Обработчик конвертации валют
    """

    data = {}
    text = message.text.split(':')
    if len(text) != 3:
        await message.reply('Данные введены в неверном формате.', reply_markup=else_or_cancel_kb)
        await States.else_or_cancel.set()
    else:
        data.update({'to': text[0], 'from': text[1], 'amount': text[2]})
        wait_message = await message.answer('Ожидаем ответ от сервера...')
        conversion = await currency_conversion_api.get_conversion(data)
        print(conversion)
        await wait_message.delete()
        if conversion.get('error'):
            print('a')
            if conversion['error'] == 'server_error':
                await message.reply('К сожалению, на данный момент сервер не отвечает :(')
                await state.finish()
                return
            elif conversion['error']['code'] == 'invalid_from_currency':
                await message.reply('Введена некоректная валюта FROM.', reply_markup=else_or_cancel_kb)
            elif conversion['error']['code'] == 'invalid_to_currency':
                await message.reply('Введена некоректная валюта TO.', reply_markup=else_or_cancel_kb)
            elif conversion['error']['code'] == 'invalid_conversion_amount':
                await message.answer('Введено некоректное число AMOUNT.', reply_markup=else_or_cancel_kb)
            await States.else_or_cancel.set()
        elif conversion.get('success'):
            print('b')
            result = conversion['result']
            date = conversion['date']
            to_currency = data['to'].upper()
            from_currency = data['from'].upper()
            amount = data['amount']
            conversion_message = (f'Конвертация прошла упешно!\n'
                                  f'Валюты: {from_currency} -> {to_currency}\n'
                                  f'Количество монет: {amount} {from_currency}\n'
                                  f'Результат: {result:.2f} {to_currency}\n'
                                  f'Дата конвертации: {date}'
                                  )
            await message.answer(conversion_message)
            await state.finish()


async def get_animal_image(message: types.Message):
    """
    Обработчик отправки фото животного
    """

    image = await animal_api.get_animal()
    await message.answer_photo(image, reply_markup=else_or_cancel_kb)
    await States.else_or_cancel.set()


async def make_poll(message: types.Message, state: FSMContext):
    """
    Обработчик создания опроса
    """

    data = await poll_validator(message.text)

    if data.get('error'):
        await message.answer(data.get('description'))
        await States.else_or_cancel.set()
    else:
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
            await message.answer('Неанонимные опросы нельзя отправлять в чаты канала',
                                 reply_markup=else_or_cancel_kb)
            await States.else_or_cancel.set()


async def else_or_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик колбэка с отмена/повторить
    """

    async with state.proxy() as data:
        data["else_or_cancel"] = callback_query.data
    if data["else_or_cancel"] == 'отмена':
        await state.finish()
        if data['type_callback'] == 'животное':
            await callback_query.message.edit_reply_markup(reply_markup=None)
            return
    elif data["else_or_cancel"] == 'повторить':
        if data['type_callback'] == 'погода':
            await States.weather.set()
            await callback_query.message.answer('Введите название города еще раз:')
        elif data['type_callback'] == 'валюта':
            await States.currency_conversion.set()
            await callback_query.message.answer('Введите данные для конвертации еще раз:')
        elif data['type_callback'] == 'животное':
            await callback_query.message.edit_reply_markup(reply_markup=None)
            await get_animal_image(callback_query.message)
            return
        elif data['type_callback'] == 'опрос':
            await States.make_poll.set()
            await callback_query.message.answer('Введите данные для опроса еще раз:')
    await callback_query.message.delete()

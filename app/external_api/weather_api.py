import os

from dotenv import load_dotenv
from aiohttp import ClientSession


load_dotenv()

API_KEY = os.getenv("OPEN_WEATHER_API_KEY")


async def get_weather(city):
    """
    Получение погоды
    """

    async with ClientSession() as session:
        url = (f'http://api.openweathermap.org/data/2.5/weather?q={city}&'
               f'appid={API_KEY}&units=metric&lang=ru')

        try:
            async with session.get(url=url) as response:
                weather_json = await response.json()
                return weather_json
        except Exception as ex:
            return {'cod': 'server_error', 'error_ex': ex}

import os

from aiohttp import ClientSession
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv('CURRENCY_CONVERSION_API')


async def get_conversion(data: dict):
    to_currency = data['to']
    from_currency = data['from']
    amount = data['amount']
    async with ClientSession() as session:
        url = (f'https://api.apilayer.com/exchangerate_data/convert?'
               f'to={to_currency}&from={from_currency}&amount={amount}'
               f'&apikey={API_KEY}')
        try:
            async with session.get(url) as response:
                print(response.status)
                currency_json = await response.json()
                print(currency_json)
                return currency_json
        except Exception as ex:
            return {'error': 'server_error', 'error_ex': ex}

import random

from aiohttp import ClientSession


async def get_animal_image():
    """
    Обращаемся к API с картинками животных и получаем картинку
    """

    animals_urls = {
        'dog': 'https://random.dog/woof.json',
        'fox': 'https://randomfox.ca/floof/',
    }

    animal_random_choice = random.choice(list(animals_urls.keys()))

    async with ClientSession() as session:
        url = animals_urls[animal_random_choice]

        try:
            async with session.get(url) as response:
                animal = await response.json()
                if animal.get('url'):
                    return animal.get('url')
                elif animal.get('link'):
                    return animal.get('link')
        except Exception as ex:
            return {'error': 'server_error', 'error_ex': ex}

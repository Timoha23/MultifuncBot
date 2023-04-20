## Multifunctional Bot
### Описание
---
Данный проект представляет собой многофункционального бота. 

### Используемые технологии
---
* Python 3.10.6;
* Aiogram 2.22.2;
* Aiohttp 3.8.4.

### О проекте
---

<details>
<summary>ТЗ проекта ↓</summary>
Напишите телеграмм-бота на языке Python, который будет выполнять следующие функции:

1. Приветствовать пользователя и предлагать ему выбрать определенную функцию бота.
2. Определить текущую погоду в определенном городе, используя публичное API погоды (например, OpenWeatherMap) и выдавать пользователю соответствующую информацию.
3. Конвертировать валюты, используя публичное API курсов валют (например, Exchange Rates API) и предоставлять пользователю результат конвертации.
4. Отправлять случайную картинку с милыми животными
5. Создавать опросы (polls) и отправлять их в групповой чат с определенным вопросом и вариантами ответов.
</details>

Функции проекта:
<details>
- Определение текущий погоды:

![gif](https://user-images.githubusercontent.com/103051349/233333236-a328735b-6ee9-41ef-83cf-388170e5f85d.gif)
- Конвертация валют:

![gif](https://user-images.githubusercontent.com/103051349/233334299-31d5c80a-b18c-4b42-a7de-0d34faf0ad59.gif)
- Отправка картинки с милым животным:

![gif](https://user-images.githubusercontent.com/103051349/233334395-ec9f2bee-f77c-4481-9977-372fc6303d3f.gif)
- Создание опроса:

![gif](https://user-images.githubusercontent.com/103051349/233334575-ed414136-86c8-4d27-8757-f87746e7462a.gif)
### Запуск проекта
---
1. Клонируем:
``` git clone https://github.com/Timoha23/MultifuncBot.git ```
2. Устанавливаем venv:
``` python -m venv venv ```
3. Активируем venv:
``` source venv/Scripts/activate ```
4. Устанавливаем зависимости из requirements.txt
``` pip install -r requirements.txt ```
5. Создаем файл .env и заполняем его в соответсвии с примером (.env.example):
6. Запускаем бота:
``` python app/bot.py ```

### Используемые API
---
- Погода - http://api.openweathermap.org
- Конвертер валют - https://api.apilayer.com
- Животные - https://random.dog и https://randomfox.ca

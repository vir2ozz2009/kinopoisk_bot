"""Кастомные запросы к API."""

import logging
import os
from logging import StreamHandler

import aiohttp
from dotenv import load_dotenv

load_dotenv()

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)

kinopoisk_token = os.getenv('KINOPOISK_TOKEN2')


headers = {
    'accept': 'application/json',
    'X-API-KEY': kinopoisk_token
}


class Request():
    """Кастомные запросы к эндпоинтам."""

    async def get_response_random_film(self, headers):
        """Запрос на рандомный фильм."""
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                'https://api.kinopoisk.dev/v1.3/movie/random'
            ) as resp:
                if resp.status != 200:
                    logger.error(f'Сервер вернул ответ: {resp.status}')
                response = await resp.json()
            logger.debug(response)
        return response

    async def get_response_film(self, headers, message):
        """Запрос на поиск фильма по названию."""
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                f'https://api.kinopoisk.dev/v1.3/movie?page=1&limit=10&name={str(message)}'
            ) as resp:
                if resp.status != 200:
                    logger.error(f'Сервер вернул ответ: {resp.status}')
                response = await resp.json()
            logger.debug(response)
        return response

    async def get_gilm_by_parameters(self, headers, message):
        """Запрос на поиск фильма по параметрам - жанр, тип."""
        genre, tip = message
        url = f'https://api.kinopoisk.dev/v1.3/movie?page=1&limit=10&type={tip}&genres.name={genre}'
        logger.debug(url)
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f'Сервер вернул ответ: {resp.status}')
                response = await resp.json()
            logger.debug(response)
        return response

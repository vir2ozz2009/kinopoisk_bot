"""Выбор информации о фильме из JSON"""

import logging
import os
from logging import StreamHandler
from typing import Tuple

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from custom_requests import Request
from genre_list import GenreList

load_dotenv()

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)

KINOPOISK_ID_URL = 'https://www.kinopoisk.ru/film/'

kinopoisk_token = os.getenv('KINOPOISK_TOKEN2')

headers = {
    'accept': 'application/json',
    'X-API-KEY': kinopoisk_token
}


class FindInfoToShow():
    """Функции поиска данных."""

    def __init__(
            self,
            obj: dict,
            to_find: str = '',
            headers=headers,
            name: str = 'name',
            message: str = ''
    ) -> None:
        self.obj = obj
        self.to_find = to_find
        self.name = name
        self.headers = headers

    def info_to_show(self) -> list:
        """Функция поиска."""
        result_list = []
        if len(self.obj['docs']) >= 10:
            length = 10
        elif 5 < len(self.obj['docs']) < 10:
            length = 5
        else:
            length = len(self.obj['docs'])
        for i in range(0, length):
            res = self.obj['docs'][i][f'{self.to_find}']
            if isinstance(res, str):
                result_list.append(res)
            if isinstance(res, list):
                res = res[0][self.name]
                result_list.append(res)
        return result_list

    def get_films_id(self) -> list:
        """
        Список найденных элементов если содержатся в списке словарей
        с одним именем, например:
        "genres":
        [{"name": "короткометражка"},
        {"name": "боевик"}]
        ."""
        result_list = []
        if len(self.obj['docs']) >= 10:
            length = 10
        elif 5 < len(self.obj['docs']) < 10:
            length = 5
        else:
            length = len(self.obj['docs'])
        for i in range(0, length):
            res = self.obj['docs'][i]['id']
            if isinstance(res, int):
                result_list.append(res)
            if isinstance(res, str):
                result_list.append(res)
            if isinstance(res, list):
                res = res[0][self.name]
                result_list.append(res)
        return result_list

    async def get_one_random_film(self) -> Tuple[str, str]:
        """Один рандомный фильм + постер."""
        film = await Request.get_response_random_film(self, headers)
        logger.debug(film)
        name = film["name"]
        rating_kp = film["rating"]["kp"]
        genre = film["genres"][0]["name"]
        length = film["movieLength"]
        short_description = film['shortDescription']
        text = f'''Советую фильм:
"{name}".
Его рейтинг на КП: {rating_kp}.
Жанр: {genre}.
Краткое описание: {short_description}.
Длительность: {length} минут.
'''
        poster = film["poster"]["url"]
        return (text, poster)

    async def get_one_or_more_films(
            self, message: str
    ) -> Tuple[str, str, InlineKeyboardButton, str]:
        """Один или несколько фильмов."""
        film: dict = await Request.get_response_film(self, headers, message)
        keyboard = None
        if film['total'] > 1:
            how_much_films: str = 'many'
            names = FindInfoToShow(film, 'name').info_to_show()
            films_id = FindInfoToShow(film).get_films_id()
            logger.debug(films_id)
            buttons = []

            for film_name, film_id in zip(names, films_id):
                button = InlineKeyboardButton(
                    text=film_name,
                    url=f'{KINOPOISK_ID_URL}{film_id}'
                )
                buttons.append([button])

            keyboard = InlineKeyboardMarkup(buttons)
            text = "Нашлось несколько фильмов. Выберите фильм из списка:"
            poster = ''
            return (text, how_much_films, keyboard, poster)

        how_much_films = 'one'
        names = film['docs'][0]['name']
        genre = film['docs'][0]["genres"]
        genres_lst = GenreList(genre)
        genres = genres_lst.get_genre_str()
        length = film['docs'][0]["movieLength"]
        rating_kp = film['docs'][0]['rating']['kp']
        poster = film['docs'][0]['poster']['url']
        text = f'''Нашел фильм: {names}.
Его рейтинг на КП: {rating_kp}.
Жанр: {genres}.
Длительность: {length} минут.'''
        return (text, how_much_films, keyboard, poster)

    async def get_film_by_parametres(self, response: dict) -> Tuple[str, str]:
        """Возврат фильма по параметрам жанр и тип."""
        film = response
        logger.debug(film)
        name1 = film['docs'][0]['name']
        rating_kp = film['docs'][0]['rating']['kp']
        genre = film['docs'][0]["genres"]
        genres = GenreList(genre).get_genre_str()
        film_id = film['docs'][0]['id']
        link = f'https://www.kinopoisk.ru/film/{film_id}/'
        if film['docs'][0]["movieLength"] is None:
            length_to_show = 'Не указано'
        else:
            length = film['docs'][0]["movieLength"]
            length_to_show = f'{length} минут'
        text = f'''Найденный фильм: {name1}.
Его рейтинг на КП: {rating_kp}.
Жанр: {genres}.
Длительность: {length_to_show}.
{link}'''
        poster = film['docs'][0]['poster']['url']
        return (text, poster)

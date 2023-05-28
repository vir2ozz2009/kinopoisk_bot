"""Основная логика работы бота Кинопоиска."""

import logging
import os
import sys
from logging import StreamHandler

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from checks import Check
from constants import COMMAND_LIST, FILM_GENRE_BUTTONS, FILM_TYPE_BUTTONS
from custom_requests import Request
from find_info import FindInfoToShow

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)

load_dotenv()

telegram_token = os.getenv('TELEGRAM_TOKEN')
kinopoisk_token = os.getenv('KINOPOISK_TOKEN2')

BOT_USERNAME = '@Kinopoisk1111Bot'

headers = {
    'accept': 'application/json',
    'X-API-KEY': kinopoisk_token
}

# Текущий запрос с параметрами к АПИ
info_dict = {'жанр': None, 'тип': None}


# ФУНКЦИИ БОТА
class Bot:
    """Основный функции бота."""

    def __init__(self, telegram_token, headers):
        self.telegram_token = telegram_token
        self.headers = headers
        self.app = Application.builder().token(self.telegram_token).build()
        self.start_handler = CommandHandler('start', self.start)
        self.random_film_handler = CommandHandler(
            'random_film',
            self.send_random_film_job
        )
        self.find_film_handler = CommandHandler(
            'find_film',
            self.find_film_by_name
        )
        self.find_by_params_handler = CommandHandler(
            'find_by_params',
            self.find_by_params1
        )

    def run(self):
        """Запуск бота."""
        logger.debug("Запуск бота.")
        self.app.add_handler(self.start_handler)
        self.app.add_handler(self.random_film_handler)
        self.app.add_handler(self.find_film_handler)
        self.app.add_handler(self.find_by_params_handler)

        logger.debug("Polling...")
        self.app.run_polling()

    async def start(self, update, context):
        """Запуск бота с выбором команд."""
        logger.debug("Запуск функции start.")
        buttons = ReplyKeyboardMarkup([
                    ['/random_film', 'Рандомный фильм'],
                    ['/find_film', 'Найти фильм по названию'],
                    ['/find_by_params', 'Найти фильм по параметрам']
                ])
        await update.message.reply_text(
            text='''Привет!
    Для того чтобы я посоветовал рандомный фильм нажми /random_film
    Для поиска фильма по названию нажми /find_film
    Для поиска фильма по жанру и типу нажми /find_by_params''',
            reply_markup=buttons
        )

    async def middle(self, update, context):
        """Промежуточная функция для очистки запросов."""
        info_dict['жанр'] = None
        info_dict['тип'] = None
        ConversationHandler.END
        await self.start(update, context)

    async def send_random_film_job(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
    ):
        """Запуск функции по отправке 1 рандомного фильма."""
        logger.debug("Запуск функции send_random_film_job.")
        await update.message.reply_text(text='Сейчас пришлю рандомный фильм!')
        await self.send_random_film(update, context)

    async def send_random_film(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
    ):
        """Отправка 1 рандомного фильма."""
        logger.debug("Запуск функции send_random_film.")
        logger.debug(headers)
        text, poster = await FindInfoToShow(headers).get_one_random_film()
        await update.message.reply_text(text)
        await update.message.reply_photo(poster)

    async def find_film_by_name(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
    ):
        """Поиск фильмов ПО НАЗВАНИЮ."""
        logger.debug("Запуск функции find_film_by_name.")
        await update.message.reply_text(text='Введите фильм для поиска')
        self.app.add_handler(
            MessageHandler(filters.TEXT, self.find_film2)
        )
        return ConversationHandler.END

    async def find_film2(self, update, context):
        """Продолжение поиска по названию. Если нашлось >1 то выдает список."""
        logger.debug("Запуск функции find_film_by_name2.")
        message = update.message.text
        film = await FindInfoToShow.get_one_or_more_films(self, message)
        text, how_much_films, keyboard, poster = film
        if how_much_films == 'many':
            await update.message.reply_text(text, reply_markup=keyboard)
        else:
            await update.message.reply_text(text)
            await update.message.reply_photo(poster)

    async def find_by_params1(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
    ):
        """Поиск фильма по параметрам. Выбор жанра и типа фильма."""
        logger.debug('Запуск функции поиска по парамерам.')
        genre_buttons = ReplyKeyboardMarkup(FILM_GENRE_BUTTONS)
        await update.message.reply_text(
            text='Поиск фильма по параметрам. Выберите жанр.',
            reply_markup=genre_buttons
        )
        self.app.add_handler(
            MessageHandler(filters.TEXT, self.find_by_params2)
        )

    async def find_by_params2(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
    ):
        """Выбор типа фильма."""
        logger.debug("Запуск функции find_by_params2")
        message = update.message.text
        if info_dict['жанр'] is None:
            info_dict['жанр'] = message
        logger.debug(f"'первое сообщение:', {message}, 'словарь', {info_dict}")
        type_buttons = ReplyKeyboardMarkup(FILM_TYPE_BUTTONS)
        await update.message.reply_text(
            text='Выберите тип.',
            reply_markup=type_buttons
        )

        self.app.remove_handler(
            MessageHandler(filters.TEXT, self.find_by_params2)
        )
        self.app.add_handler(
            MessageHandler(filters.TEXT, self.find_by_params_result)
        )
        return await self.find_by_params_result(update, context)

    async def find_by_params_result(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE
    ):
        """Итоговый ответ по запросу поиска по параментрам."""
        logger.debug("Запуск функции find_by_params_result")
        message = update.message.text
        info_dict['тип'] = message
        logger.debug(f"'ворое сообщение:', {message}, 'словарь', {info_dict}")
        genre = info_dict['жанр'].lower()
        tip = info_dict['тип']
        message = genre, tip

        response = await Request.get_gilm_by_parameters(self, headers, message)
        text, poster = await FindInfoToShow.get_film_by_parametres(
            self, response
        )

        await update.message.reply_text(text)
        await update.message.reply_photo(poster)

        await self.middle(update, context)


if __name__ == '__main__':

    if Check.token_check(telegram_token, kinopoisk_token) is False:
        logger.critical("Не хватает токена.")
        sys.exit('Не хватает токена.')
    logger.debug("Токены на месте.")

    bot = Bot(telegram_token, headers)
    bot.run()

import logging
from logging import StreamHandler

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)


class Check():
    """Класс проверки функций."""

    def movie_in_list(self, message: dict, movie_list_buttons: list) -> bool:
        """Проверка есть ли в сообщении название из кнопкок."""
        check_message = message['text']
        logger.debug(f'Текст сообщения: {check_message}')
        lst = []
        for i in range(0, len(movie_list_buttons) - 1):
            name = movie_list_buttons[i]
            lst.append(name[0])
        if check_message in lst:
            logger.debug(f'лист из проверки {lst}')
            return True
        logger.debug(f'лист из проверки {lst}')
        return False

    def token_check(self, *tokens) -> bool:
        """Проверка токенаов."""
        logger.debug("Проверка токена.")
        return all(tokens)

"""Составление жанров в строку из всписка."""


class GenreList():
    """Класс составления списка жанров у одного фильма."""

    def __init__(self, genre: dict) -> None:
        self.genre = genre

    def get_genre_str(self) -> str:
        """Составление текста из жанров."""
        if not self.genre:
            return ''
        genre_lst: list = [genre['name'] for genre in self.genre]
        genre_str: str = ', '.join(genre_lst)
        return genre_str

    def __str__(self):
        return self.get_genre_str()

"""Этот модуль управляет библиотекой книг, предоставляя функции для создания, удаления, поиска, просмотра и обновления статуса книг."""

import json
import library


def create(author, title, year):
    """Создает новую запись книги и добавляет её в библиотеку.

    Аргументы:
    author -- автор книги
    title -- название книги
    year -- год издания книги
    """
    try:
        with open('books.json', encoding='utf-8') as books:
            lib = json.loads(books.read())
    except (FileNotFoundError, json.JSONDecodeError):
        lib = {'max_id': 0, 'library': []}
    _id = lib["max_id"] + 1
    lib['max_id'] = _id
    book = library.Library(_id, title, author, year)
    lib['library'].append(book.display())
    with open('books.json', 'w', encoding='utf-8') as books:
        json.dump(lib, books, indent=4, ensure_ascii=False)
    return f'Книга добавлена в библиотеку. Присвоен id={_id}'


def delete_book(_id):
    """Удаляет книгу из библиотеки по её id.

    Аргументы:
    _id -- идентификатор книги, которую нужно удалить
    """
    try:
        with open('books.json', encoding='utf-8') as books:
            lib = json.loads(books.read())
        for el in range(len(lib['library'])):
            if lib['library'][el]['id'] == int(_id):
                del lib['library'][el]
                break
        with open('books.json', 'w', encoding='utf-8') as books:
            json.dump(lib, books, indent=4, ensure_ascii=False)
        return 'Книга удалена из библиотеки'
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 'Введен некоректный id. Попробуйте снова'


def search(string):
    """Ищет книги в библиотеке по автору, названию или году издания.

    Аргументы:
    string -- строка для поиска, может быть автором, названием или годом издания
    """
    try:
        with open('books.json', encoding='utf-8') as books:
            lib = json.loads(books.read())
        search_results = []
        for el in lib['library']:
            if el['author'] == string or el['title'] == string or el['year'] == string:
                search_results.append(el)
        return search_results
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 'Некоректный запрос поиска.'


def view():
    """Возвращает список всех книг в библиотеке."""
    try:
        with open('books.json', encoding='utf-8') as books:
            lib = json.loads(books.read())
        return lib['library']
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 'Ошибка чтения библиотеки'


def update(_id):
    """Обновляет статус книги в библиотеке по её id.

    Аргументы:
    _id -- идентификатор книги, статус которой нужно обновить
    """
    try:
        with open('books.json', encoding='utf-8') as books:
            lib = json.loads(books.read())
        for el in range(len(lib['library'])):
            if lib['library'][el]['id'] == int(_id):
                if lib['library'][el]['status'] == 'выдана':
                    lib['library'][el]['status'] = 'в наличии'
                else:
                    lib['library'][el]['status'] = 'выдана'
                break
        with open('books.json', 'w', encoding='utf-8') as books:
            json.dump(lib, books, indent=4, ensure_ascii=False)
        return 'Статус книги изменён'
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return 'Некоректные данные.'


def get_help():
    """Возвращает справочную информацию о библиотеке."""
    return library.Library.help()

"""Основной модуль для управления библиотечной системой."""

import function

function.get_help()

while input_data := input('Введите команду:\n'):
    if input_data.strip().lower() == 'добавить':
        title = input('Введите название:\n').strip()
        author = input('Введите автора:\n').strip()
        year = input('Введите год издания:\n').strip()
        print(function.create(author, title, year))
    elif input_data.strip().lower() == 'удалить':
        _id = input('Введите id для удаления:\n').strip()
        print(function.delete_book(_id))
    elif input_data.strip().lower() == 'поиск':
        search_string = input(
            'Введите название книги, автора или год издания:\n').strip()
        result = function.search(search_string)
        if isinstance(result, str):
            print(result)
        elif len(result) == 0:
            print('По данному запросу ничего не найдено.')
        else:
            print(f'Найдено {len(result)} книг')
            function.print_table(result)
    elif input_data.strip().lower() == 'книги':
        result = function.view()
        if isinstance(result, str):
            print(result)
        elif len(result) == 0:
            print('Библиотека пуста')
        else:
            print(f'Колличество книг в библиотеке: {len(result)}')
            function.print_table(result)
    elif input_data.strip().lower() == 'статус':
        _id = input('Введите id для обновления статуса:\n').strip()
        print(function.update(_id))
    elif input_data.strip().lower() == 'помощь':
        function.get_help()
    elif input_data.strip().lower() == 'конец':
        print('До свидания.')
        break
    else:
        print('Некоректная команда. Попробуйте ещё раз ли воспользуйтесь командой "помощь"')

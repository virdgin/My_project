class Library():

    @staticmethod
    def help():
        """Печатает справочную информацию о доступных командах."""
        print('Здравствуйте.\nДоступные команды:\n1. добавить - добавляет книгу в библиотеку.\n2. удалить - Удаляет книгу с существующим id.\n3. поиск - Произодит поиск книги по автору, названию или году\n4. книги - Показывает все книги в библиотеке.\n5. статус - обновляет статус книги по id.\n5. помощь - показывает текущую справку.\n6. конец - выходит из программы.')

    def __init__(self, _id, title, author, year, status='в наличии'):
        self.id = _id
        self.title = title
        self.author = author
        self.year = year
        self.status = status

    def display(self):
        """Возвращает информацию о книге в виде словаря."""
        return {"id": self.id, "title": self.title, "author": self.author, "year": self.year, "status": self.status}

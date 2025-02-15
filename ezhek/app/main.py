import os
import ast
from datetime import datetime

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.core.text.markup import MarkupLabel
from kivy.config import ConfigParser
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.event import EventDispatcher
from numpy import multiply
from pandas import read_excel, ExcelWriter, DataFrame
import re


class MainMenu(Screen):
    """Класс главного меню приложения."""

    def __init__(self, **kw):
        """Инициализация главного меню."""
        super(MainMenu, self).__init__(**kw)
        box = BoxLayout(orientation='vertical')
        box.add_widget(
            Button(text='Лекарства', on_press=lambda x: set_screen('medicines')))
        box.add_widget(
            Button(text='Врачи', on_press=lambda x: set_screen('doctors')))
        self.add_widget(box)


class Medicines(Screen):
    """Класс для работы с лекарствами."""

    def __init__(self, **kwargs):
        """Инициализация класса Medicines."""
        super(Medicines, self).__init__(**kwargs)

    def read_ex(self):
        """Читает данные о лекарствах из Excel файла."""
        df = read_excel('.\medicines.xlsx')
        self.dict_list = df.to_dict(orient='records')
        self.pharma = []
        for el in self.dict_list:
            for key, value in el.items():
                if key == '#Название':
                    self.pharma.append(value)

    def on_enter(self):
        """Создает интерфейс при входе на экран."""
        self.table = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.table.bind(minimum_height=self.table.setter('height'))
        back_btn = Button(text='В главное меню',
                          on_press=lambda x: set_screen('main_menu'), size_hint_y=None, height=dp(40))
        self.table.add_widget(back_btn)
        self.txt = TextInput(hint_text='Введите...', text='',
                             size_hint_y=None, height=dp(40))
        self.txt.bind(text=self.on_text)
        self.table.add_widget(self.txt)
        self.add_widget(self.table)

    def on_text(self, *args):
        """Обрабатывает поиск по введенному тексту."""
        self.grid.clear_widgets()
        data = self.txt.text


class Doctors(Screen):
    """Класс для работы с информацией о врачах."""

    def read_ex(self):
        """Читает данные о врачах из Excel файла."""
        try:
            df = read_excel(os.path.join('doctors.xlsx'))
            self.dict_list = df.to_dict(orient='records')
        except:
            col = ['#Фамилия', '#Имя', '#Отчество', '#Место работы', '#Дата последнего визита',
                   '#Опыт', '#Потенциал', '#Договорённости', '#Примечание']
            df = DataFrame(columns=col)
            excel = ExcelWriter('doctors.xlsx', engine='xlsxwriter')
            df.to_excel(excel, index=False)
            excel.save()

    def __init__(self, **kw):
        super(Doctors, self).__init__(**kw)
        # self.temp_list_doc = []

    def on_enter(self):
        """Создает интерфейс при входе на экран."""
        # self.main_table = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.table = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.table.bind(minimum_height=self.table.setter('height'))
        back_btn = Button(text='В главное меню', on_press=lambda x: set_screen(
            'main_menu'), size_hint_y=None, height=dp(40))
        new_btn = Button(text='Добавить врача',
                         on_press=self.new_doctor, size_hint_y=None, height=dp(40))
        self.table.add_widget(back_btn)
        self.table.add_widget(new_btn)
        self.txt = TextInput(hint_text='Введите...', text='',
                             size_hint_y=None, height=dp(40))
        self.txt.bind(text=self.on_text)
        self.table.add_widget(self.txt)
        # self.main_table.add_widget(self.table)
        root = RecycleView(size_hint=(1, 1), size=(
            Window.width, Window.height))
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.table.add_widget(self.grid)
        root.add_widget(self.table)
        self.add_widget(root)
        self.read_ex()

    def new_doctor(self, *args):
        """Инициирует создание нового врача, очищая список и инициализируя словарь."""
        self.grid.clear_widgets()
        self.doctor_dict = {}
        self.read_ex()
        for el in self.dict_list:
            for key in el:
                self.doctor_dict[key] = ''
        self.get_new_doctor()

    def get_new_doctor(self, *args):
        """Отображает форму для ввода данных нового врача."""
        self.table.remove_widget(self.txt)
        self.grid.clear_widgets()
        for key, value in self.doctor_dict.items():
            self.grid.add_widget(Button(text=f'[b]{key[1:]}[/b]: {value}', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.put_new_doctor))
        self.grid.add_widget(Button(text='Сохранить', size_hint_y=None,
                                    height=dp(40), on_press=self.save_doctor))

    def save_doctor(self, *args):
        """Сохраняет данные нового врача в список и файл."""
        self.dict_list.append(self.doctor_dict)
        self.write_exсel()
        self.clear_widgets()
        self.on_enter()

    def put_new_doctor(self, *args):
        """Обрабатывает ввод данных для нового врача."""
        data = args[0].text
        data = data.split(':')
        data[0] = '#' + data[0][3:-4]
        if data[0] == '#Дата последнего визита':
            self.doctor_dict[data[0]] = datetime.now().strftime('%d %B %Y')
            self.get_new_doctor()
        else:
            self.grid.clear_widgets()
            self.label = Label(
                text=f'[b]{data[0][1:]}[/b]', text_size=(150, None), markup=True)
            self.grid.add_widget(self.label)
            self.text_update = TextInput(
                text=data[1], multiline=True, size_hint_y=None, height=dp(40))
            self.grid.add_widget(self.text_update)
            self.grid.add_widget(Button(text='Назад', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.get_new_doctor))
            self.grid.add_widget(Button(text='Сохранить', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.get_new_doctor_info))

    def get_new_doctor_info(self, *args):
        """Сохраняет введенную информацию о враче."""
        text = '#' + self.label.text[3:-4]
        self.doctor_dict[text] = self.text_update.text.upper()
        self.write_exсel()
        self.get_new_doctor()

    def on_text(self, *args):
        """Обрабатывает поиск по введенному тексту."""
        self.grid.clear_widgets()
        data = self.txt.text
        temp_list_doc = set()
        for el in self.dict_list:
            if data.lower() in el['#Фамилия'].lower() or data.lower() in el['#Место работы'].lower():
                temp_list_doc.add(
                    f'{el['#Фамилия']} {el['#Имя']} {el['#Отчество']}')
                temp_list_doc.add(el['#Место работы'])
        for el in temp_list_doc:
            btn_doc = Button(text=el, size_hint_y=None,
                             height=dp(40), on_press=self.choices)
            self.grid.add_widget(btn_doc)

    def choices(self, *args):
        """Обрабатывает выбор врача из списка."""
        self.grid.clear_widgets()
        data = args[0].text
        self.temp_set = []
        for el in self.dict_list:
            if f'{el['#Фамилия']} {el['#Имя']} {el['#Отчество']}' == data:
                self.temp_set.append(el)
                self.output_doctors()
            if el['#Место работы'] == data:
                self.search_work(data)

    def search_work(self, *args):
        """Отображает результаты поиска по месту работы"""
        self.table.remove_widget(self.txt)
        self.grid.clear_widgets()
        data = args[0]
        for el in self.dict_list:
            if el['#Место работы'].lower() == data.lower():
                self.grid.add_widget(Button(text=f'{el['#Фамилия']} {el['#Имя']} {el['#Отчество']}', size_hint_y=None,
                                            height=dp(40), markup=True, on_press=self.choices))
                

    def output_doctors(self, *args):
        """Отображает информацию о выбранном враче."""
        self.table.remove_widget(self.txt)
        self.grid.clear_widgets()
        for el in self.temp_set:
            for key, value in el.items():
                self.grid.add_widget(Button(text=f'[b]{key[1:]}[/b]: {value}', size_hint_y=None,
                                            height=dp(40), markup=True, on_press=self.put_doctors))

    def put_doctors(self, *args):
        """Обрабатывает редактирование данных существующего врача."""
        data = args[0].text
        data = data.split(':')
        data[0] = '#' + data[0][3:-4]
        if data[0] == '#Дата последнего визита':
            for el in self.dict_list:
                if el == self.temp_set[0]:
                    el[data[0]] = datetime.now().strftime('%d %B %Y')
                    break
            self.write_exсel()
            self.output_doctors()
        elif data[0] in ['#Опыт', '#Договорённости', '#Примечание', '#Потенциал']:
            self.grid.clear_widgets()
            self.label = Label(
                text=f'[b]{data[0][1:]}[/b]', text_size=(150, None), markup=True)
            self.grid.add_widget(self.label)
            self.text_update = TextInput(
                text=data[1], multiline=True, size_hint_y=None, height=dp(40))
            self.grid.add_widget(self.text_update)
            self.grid.add_widget(Button(text='Назад', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.output_doctors))
            self.grid.add_widget(Button(text='Обновить', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.get_info))

    def get_info(self, *args):
        """Сохраняет обновленную информацию о враче."""
        text = '#' + self.label.text[3:-4]
        for el in self.dict_list:
            if el == self.temp_set[0]:
                el[text] = self.text_update.text
                break
        self.write_exсel()
        self.output_doctors()

    def write_exсel(self, *args):
        """Сохраняет данные в Excel файл."""
        df = DataFrame(self.dict_list)
        exсel = ExcelWriter('doctors.xlsx', engine='xlsxwriter')
        df.to_excel(exсel, index=False)
        exсel._save()

    def on_leave(self):
        """Очищает виджеты при выходе с экрана."""
        self.table.clear_widgets()


def set_screen(name_screen):
    """Переключает экран приложения."""
    sm.current = name_screen


sm = ScreenManager()
sm.add_widget(MainMenu(name='main_menu'))
sm.add_widget(Medicines(name='medicines'))
sm.add_widget(Doctors(name='doctors'))


class EzhekApp(App):
    """Основной класс приложения."""

    def __init__(self, **kwargs):
        """Инициализация класса EzhekApp."""
        super(EzhekApp, self).__init__(**kwargs)
        self.config = ConfigParser()

    def build(self):
        """Создает и возвращает основной виджет приложения."""
        return sm


if __name__ == '__main__':
    EzhekApp().run()

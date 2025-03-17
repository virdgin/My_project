"""Основной модуль приложения для управления данными о врачах и аптеках."""

import os
import csv
from datetime import datetime
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import dp


class MainMenu(Screen):
    def __init__(self, **kw):
        super(MainMenu, self).__init__(**kw)
        box = BoxLayout(orientation='vertical')
        box.add_widget(
            Button(text='Аптеки', on_press=lambda x: set_screen('pharmacies')))
        box.add_widget(
            Button(text='Врачи', on_press=lambda x: set_screen('doctors')))
        self.add_widget(box)


class Pharmacies(Screen):
    def read_csv(self):
        """Читает данные о аптеках из CSV файла."""
        try:
            app = App.get_running_app()
            file_path = os.path.join(app.user_data_dir, 'pharmacies.csv')

            self.dict_list = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    self.dict_list = list(reader)

        except Exception as e:
            self.dict_list = []

    def __init__(self, **kwargs):
        super(Pharmacies, self).__init__(**kwargs)

    def on_enter(self):
        self.table = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.table.bind(minimum_height=self.table.setter('height'))
        back_btn = Button(text='В главное меню', on_press=lambda x: set_screen(
            'main_menu'), size_hint_y=None, height=dp(40))
        new_btn = Button(
            text='Добавить аптеку', on_press=self.new_pharmacies, size_hint_y=None, height=dp(40))
        self.table.add_widget(back_btn)
        self.table.add_widget(new_btn)
        self.txt = TextInput(hint_text='Введите...', text='',
                             size_hint_y=None, height=dp(40))
        self.txt.bind(text=self.on_text)
        self.table.add_widget(self.txt)
        root = RecycleView(size_hint=(1, 1), size=(
            Window.width, Window.height))
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.table.add_widget(self.grid)
        root.add_widget(self.table)
        self.add_widget(root)
        self.read_csv()

    def new_pharmacies(self, *args):
        self.grid.clear_widgets()
        self.pharma_dict = {}
        self.read_csv()
        if len(self.dict_list) == 0:
            for i in ['#Название', '#Адрес', '#Наличие', '#Договорённости', '#Дата последнего визита']:
                self.pharma_dict[i] = ''
        else:
            for el in self.dict_list:
                for key in el:
                    self.pharma_dict[key] = ''
        self.get_new_pharma()

    def get_new_pharma(self, *args):
        self.table.remove_widget(self.txt)
        self.grid.clear_widgets()
        for key, value in self.pharma_dict.items():
            self.grid.add_widget(Button(text=f'[b]{key[1:]}[/b]:\n{value}', size_hint_y=None,
                                        height=dp(40), text_size=(None, None), markup=True, on_press=self.put_new_pharma))
        self.grid.add_widget(Button(text='Сохранить', size_hint_y=None,
                                    height=dp(40), on_press=self.save_pharma))

    def save_pharma(self, *args):
        self.dict_list.append(self.pharma_dict)
        self.write_csv()
        self.clear_widgets()
        self.on_enter()

    def put_new_pharma(self, *args):
        data = args[0].text
        data = data.split(':')
        data[0] = '#' + data[0][3:-4]
        if data[0] == '#Дата последнего визита':
            self.pharma_dict[data[0]] = datetime.now().strftime('%d %B %Y')
            self.get_new_pharma()
        else:
            self.grid.clear_widgets()
            self.label = Label(
                text=f'[b]{data[0][1:]}[/b]',  font_size=dp(20), text_size=(None, None), markup=True, size_hint_y=None)
            self.grid.add_widget(self.label)
            self.text_update = TextInput(
                text=data[1], multiline=True, size_hint_y=None, height=dp(40))
            self.grid.add_widget(self.text_update)
            self.grid.add_widget(Button(text='Сохранить', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.get_new_pharma_info))
            self.grid.add_widget(Button(text='Назад', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.get_new_pharma))

    def get_new_pharma_info(self, *args):
        text = '#' + self.label.text[3:-4]
        self.pharma_dict[text] = self.text_update.text.strip()
        self.write_csv()
        self.get_new_pharma()

    def on_text(self, *args):
        self.grid.clear_widgets()
        data = self.txt.text
        temp_list_pharma = set()
        for el in self.dict_list:
            if data.lower() in el['#Адрес'].lower():
                temp = f"{el['#Название']}\n{el['#Адрес']}"
                temp_list_pharma.add(temp)
        for el in temp_list_pharma:
            btn_pharm = Button(text=el, size_hint_y=None,
                               height=dp(40), text_size=(None, None), on_press=self.choices)
            self.grid.add_widget(btn_pharm)

    def choices(self, *args):
        self.grid.clear_widgets()
        data = args[0].text
        self.temp_set = []
        for el in self.dict_list:
            if f"{el['#Название']}\n{el['#Адрес']}" == data:
                self.temp_set.append(el)
                self.output_pharmacies()

    def output_pharmacies(self, *args):
        self.table.remove_widget(self.txt)
        self.grid.clear_widgets()
        for el in self.temp_set:
            for key, value in el.items():
                self.grid.add_widget(Button(text=f'[b]{key[1:]}[/b]:\n{value}', size_hint_y=None,
                                            height=dp(40), markup=True, text_size=(None, None), on_press=self.put_pharma))

    def put_pharma(self, *args):
        data = args[0].text
        data = data.split(':')
        data[0] = '#' + data[0][3:-4]
        if data[0] == '#Дата последнего визита':
            for el in self.dict_list:
                if el == self.temp_set[0]:
                    el[data[0]] = datetime.now().strftime('%d %B %Y')
                    break
            self.write_csv()
            self.output_pharmacies()
        else:
            self.grid.clear_widgets()
            self.label = Label(
                text=f'[b]{data[0][1:]}[/b]',  font_size=dp(20), text_size=(None, None), markup=True, size_hint_y=None)
            self.grid.add_widget(self.label)
            self.text_update = TextInput(
                text=data[1], multiline=True, size_hint_y=None, height=dp(40))
            self.grid.add_widget(self.text_update)
            self.grid.add_widget(Button(text='Назад', size_hint_y=None,
                                        height=dp(40), markup=True, text_size=(None, None), on_press=self.output_pharmacies))
            self.grid.add_widget(Button(text='Обновить', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.get_info))

    def get_info(self, *args):
        text = '#' + self.label.text[3:-4]
        for el in self.dict_list:
            if el == self.temp_set[0]:
                el[text] = self.text_update.text.strip()
                break
        self.write_csv()
        self.output_pharmacies()

    def write_csv(self, *args):
        """Сохраняет данные в CSV файл."""
        app = App.get_running_app()
        file_path = os.path.join(app.user_data_dir, 'pharmacies.csv')
        fieldnames = self.dict_list[0].keys() if self.dict_list else [
            '#Название', '#Адрес', '#Наличие', '#Договорённости', '#Дата последнего визита']
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.dict_list)

    def on_leave(self):
        self.table.clear_widgets()


class Doctors(Screen):
    def read_csv(self):
        """Читает данные о врачах из CSV файла."""
        try:
            app = App.get_running_app()
            file_path = os.path.join(app.user_data_dir, 'doctors.csv')
            # file_path = 'doctors.csv'
            self.dict_list = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    self.dict_list = list(reader)
            for el in self.dict_list:
                el.setdefault('#Специальность', '')
                el.setdefault('#Конкуренты', '')

        except Exception as e:
            self.dict_list = []

    def __init__(self, **kw):
        super(Doctors, self).__init__(**kw)

    def on_enter(self):
        self.table = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.table.bind(minimum_height=self.table.setter('height'))
        back_btn = Button(text='В главное меню', on_press=lambda x: set_screen(
            'main_menu'), size_hint_y=None, height=dp(40))
        new_btn = Button(
            text='Добавить врача', on_press=self.new_doctor, size_hint_y=None, height=dp(40))
        self.table.add_widget(back_btn)
        self.table.add_widget(new_btn)
        self.txt = TextInput(hint_text='Введите...',
                             text='', size_hint_y=None, height=dp(40))
        self.txt.bind(text=self.on_text)
        self.table.add_widget(self.txt)
        root = RecycleView(size_hint=(1, 1), size=(
            Window.width, Window.height))
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.table.add_widget(self.grid)
        root.add_widget(self.table)
        self.add_widget(root)
        self.read_csv()

    def new_doctor(self, *args):
        self.grid.clear_widgets()
        self.doctor_dict = {}
        self.read_csv()
        if len(self.dict_list) == 0:
            for i in ['#Фамилия', '#Имя', '#Отчество', '#Специальность', '#Место работы', '#Опыт',
                      '#Потенциал', '#Договорённости', '#Примечание', '#Дата последнего визита', '#Конкуренты']:
                self.doctor_dict[i] = ''
        else:
            for el in self.dict_list:
                for key in el:
                    self.doctor_dict[key] = ''
        self.get_new_doctor()

    def get_new_doctor(self, *args):
        self.table.remove_widget(self.txt)
        self.grid.clear_widgets()
        for key, value in self.doctor_dict.items():
            self.grid.add_widget(Button(text=f'[b]{key[1:]}[/b]:\n{value}', size_hint_y=None,
                                        height=dp(40), markup=True, text_size=(None, None), on_press=self.put_new_doctor))
        self.grid.add_widget(Button(text='Сохранить', size_hint_y=None,
                                    height=dp(40), on_press=self.save_doctor))

    def save_doctor(self, *args):
        self.dict_list.append(self.doctor_dict)
        self.write_csv()
        self.clear_widgets()
        self.on_enter()

    def put_new_doctor(self, *args):
        data = args[0].text
        data = data.split(':')
        data[0] = '#' + data[0][3:-4]
        if data[0] == '#Дата последнего визита':
            self.doctor_dict[data[0]] = datetime.now().strftime('%d %B %Y')
            self.get_new_doctor()
        else:
            self.grid.clear_widgets()
            self.label = Label(
                text=f'[b]{data[0][1:]}[/b]', font_size=dp(20), text_size=(None, None), markup=True, size_hint_y=None)
            self.grid.add_widget(self.label)
            if data[0] == '#Примечание':
                self.text_update = TextInput(
                    text=data[1], multiline=True, size_hint_y=None, height=dp(40))
            else:
                self.text_update = TextInput(
                    text=data[1], multiline=False, size_hint_y=None, height=dp(40))
            self.grid.add_widget(self.text_update)
            self.grid.add_widget(Button(text='Сохранить', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.get_new_doctor_info))
            self.grid.add_widget(Button(text='Назад', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.get_new_doctor))

    def get_new_doctor_info(self, *args):
        text = '#' + self.label.text[3:-4]
        self.doctor_dict[text] = self.text_update.text.strip()
        self.get_new_doctor()

    def on_text(self, *args):
        self.grid.clear_widgets()
        data = self.txt.text
        temp_list_doc = set()
        for el in self.dict_list:
            if data.lower() in el['#Фамилия'].lower() or data.lower() in el['#Место работы'].lower():
                temp = f"{el['#Фамилия']} {el['#Имя']} {el['#Отчество']}"
                temp_list_doc.add(temp)
                temp_list_doc.add(el['#Место работы'])
        for el in temp_list_doc:
            btn_doc = Button(text=el, size_hint_y=None,
                             height=dp(40), on_press=self.choices)
            self.grid.add_widget(btn_doc)

    def choices(self, *args):
        self.grid.clear_widgets()
        data = args[0].text
        self.temp_set = []
        for el in self.dict_list:
            if f"{el['#Фамилия']} {el['#Имя']} {el['#Отчество']}" == data:
                self.temp_set.append(el)
                self.output_doctors()
            if el['#Место работы'] == data:
                self.search_work(data)

    def search_work(self, *args):
        self.table.remove_widget(self.txt)
        self.grid.clear_widgets()
        data = args[0]
        for el in self.dict_list:
            if el['#Место работы'].lower() == data.lower():
                self.grid.add_widget(Button(text=f"{el['#Фамилия']} {el['#Имя']} {el['#Отчество']}", size_hint_y=None,
                                            height=dp(50), markup=True, text_size=(None, None), on_press=self.choices))

    def output_doctors(self, *args):
        self.table.remove_widget(self.txt)
        self.grid.clear_widgets()
        for el in self.temp_set:
            for key, value in el.items():
                self.grid.add_widget(Button(text=f'[b]{key[1:]}[/b]:\n{value}', size_hint_y=None,
                                            height=dp(50), markup=True, text_size=(None, None), on_press=self.put_doctors))
        self.grid.add_widget(Button(text='Назад', size_hint_y=None,
                                    height=dp(40), markup=True, on_press=self.back))

    def back(self, *args):
        self.clear_widgets()
        self.on_enter()

    def put_doctors(self, *args):
        data = args[0].text
        data = data.split(':')
        data[0] = '#' + data[0][3:-4]
        if data[0] == '#Дата последнего визита':
            for el in self.dict_list:
                if el == self.temp_set[0]:
                    el[data[0]] = datetime.now().strftime('%d %B %Y')
                    break
            self.write_csv()
            self.output_doctors()
        # elif data[0] in ['#Место работы', '#Опыт',  '#Потенциал', '#Договорённости', '#Примечание', '#Специальность', '#Конкуренты']:
        else:
            self.grid.clear_widgets()
            self.label = Label(
                text=f'[b]{data[0][1:]}[/b]', font_size=dp(20), text_size=(None, None), markup=True, size_hint_y=None)
            self.grid.add_widget(self.label)
            if data[0] == '#Примечание':
                self.text_update = TextInput(
                    text=data[1], multiline=True, size_hint_y=None, height=dp(40))
            else:
                self.text_update = TextInput(
                    text=data[1], multiline=False, size_hint_y=None, height=dp(40))
            self.grid.add_widget(self.text_update)
            self.grid.add_widget(Button(text='Назад', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.output_doctors))
            self.grid.add_widget(Button(text='Обновить', size_hint_y=None,
                                        height=dp(40), markup=True, on_press=self.get_info))

    def get_info(self, *args):
        text = '#' + self.label.text[3:-4]
        for el in self.dict_list:
            if el == self.temp_set[0]:
                el[text] = self.text_update.text.strip()
                break
        self.write_csv()
        self.output_doctors()

    def write_csv(self, *args):
        """Сохраняет данные в CSV файл."""
        app = App.get_running_app()
        file_path = os.path.join(app.user_data_dir, 'doctors.csv')
        # file_path = 'doctors.csv'
        temp_dict = {'#Фамилия': '', '#Имя': '', '#Отчество': '', '#Специальность': '', '#Место работы': '', '#Опыт': '',
                     '#Потенциал': '', '#Договорённости': '', '#Примечание': '', '#Дата последнего визита': '', '#Конкуренты': ''}
        temp_list = []
        for el in self.dict_list:
            for elem in temp_dict.keys():
                temp_dict[elem] = el[elem]
            temp_list.append(temp_dict)
        self.dict_list = temp_list
        fieldnames = self.dict_list[0].keys() if self.dict_list else [
            '#Фамилия', '#Имя', '#Отчество', '#Специальность', '#Место работы', '#Опыт',
            '#Потенциал', '#Договорённости', '#Примечание', '#Дата последнего визита', '#Конкуренты']
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.dict_list)

    def on_leave(self):
        self.table.clear_widgets()


def set_screen(name_screen):
    sm.current = name_screen


sm = ScreenManager()
sm.add_widget(MainMenu(name='main_menu'))
sm.add_widget(Pharmacies(name='pharmacies'))
sm.add_widget(Doctors(name='doctors'))


class EzhekApp(App):
    def __init__(self, **kwargs):
        super(EzhekApp, self).__init__(**kwargs)
        self.config = ConfigParser()

    def build(self):
        return sm


if __name__ == '__main__':
    EzhekApp().run()

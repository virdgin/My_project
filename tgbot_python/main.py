import os
# from background import keep_alive
import telebot
from telebot import types
import data


bot = telebot.TeleBot('')
id_city = None
id_hospital = None
id_pharmacy = None
id_drug = None
id_problems = None


@bot.message_handler(commands=['start'])
def start(message):
    cites = data.get_cites()
    keyword = types.ReplyKeyboardMarkup()
    keyword.row_width = 3
    for i in cites:
        keyword.add(types.KeyboardButton(i[1]))
    bot.send_message(message.chat.id, 'Выбери город', reply_markup=keyword)
    bot.register_next_step_handler(message, get_city, cites)


def get_city(message, cites):
    global id_city
    city = message.text
    for i in cites:
        if i[1].strip('\r') == city.strip('\r'):
            id_city = str(i[0])
            break
    keyword = types.ReplyKeyboardMarkup()
    pharmacy_btn = types.KeyboardButton('Аптеки')
    hospital_btn = types.KeyboardButton('Поликлиники')
    keyword.add(pharmacy_btn, hospital_btn)
    bot.send_message(message.chat.id, 'Выбери метод', reply_markup=keyword)
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text.lower() == 'аптеки':
        pharmacy = data.get_pharmacies(id_city)
        keyword = types.ReplyKeyboardMarkup()
        keyword.row_width = 3
        for i in pharmacy:
            keyword.add(types.KeyboardButton(i[1]))
        bot.send_message(message.chat.id, 'Выбери аптеку',
                         reply_markup=keyword)
        bot.register_next_step_handler(
            message, choices_street_pharmacy, pharmacy)
    elif message.text.lower() == 'поликлиники':
        clinics = data.get_clinic(id_city)
        keyword = types.ReplyKeyboardMarkup()
        keyword.row_width = 3
        for i in clinics:
            keyword.add(types.KeyboardButton(i[1]))
        bot.send_message(message.chat.id, 'Выбери поликлинику',
                         reply_markup=keyword)
        bot.register_next_step_handler(message, get_city)


def choices_street_pharmacy(message, pharma):
    street_pharmacy = []
    for i in pharma:
        if i[1].lower() == message.text.lower():
            street_pharmacy.append(i)
    bot.send_message(message.chat.id, 'Введите улицу, дом. Через пробел')
    bot.register_next_step_handler(message, view_drugs, street_pharmacy)


def view_drugs(message, street_pharmacy):
    global id_pharmacy
    street, home = message.text.lower().split()
    for i in street_pharmacy:
        if i[3].lower() == street and i[4].lower() == home:
            id_pharmacy = str(i[0])
            break
    drugs = data.get_drugs(id_pharmacy)
    keyword = types.ReplyKeyboardMarkup()
    keyword.row_width = 3
    for i in drugs:
        keyword.add(types.KeyboardButton(i[1]))
    bot.send_message(message.chat.id, 'Выбери лекарство',
                     reply_markup=keyword)
    bot.register_next_step_handler(message, view_problem, drugs)


def view_problem(message, drugs=None):
    drug = message.text
    global id_drug
    id_problem = None
    text = ''
    for i in drugs:
        if i[1].lower() == drug.lower():
            id_drug = i[0]
            id_problem = i[3]
            break
    keyword = types.ReplyKeyboardMarkup()
    if id_problem == 0:
        text = 'Проблем нет. Обозначить проблему?'
    else:
        text = f'Проблема: {data.get_problem(id_problem)}. Обновить проблему?'
    keyword.add(types.KeyboardButton('Да'),
                types.KeyboardButton('Посмотреть комментарии'))
    bot.send_message(message.chat.id, text, reply_markup=keyword)
    bot.register_next_step_handler(message, view_comment)


def view_comment(message):
    text = message.text
    if text.lower() == 'да':
        pass
    else:
        comments = data.get_comments(id_drug)
        text = ''
        keyword = types.ReplyKeyboardMarkup()
        if len(comments) == 0:
            text = 'Коментариев нет. Добавить?'
        else:
            for el in comments:
                text += f'{el[0]} от {el[2]}: \n{el[1]}\n'
        keyword.add(types.KeyboardButton('Добавить комментарий'),
                    types.KeyboardButton('В начало'))
        bot.send_message(message.chat.id, text, reply_markup=keyword)
        bot.register_next_step_handler(message, comment)


def comment(message):
    text = message.text
    if text.lower() == 'в начало':
        start(message)
    user = {
        'id_drug': id_drug,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }
    bot.send_message(
        message.chat.id, 'Напишите комментарий. Затем нажмите отправить.')
    bot.register_next_step_handler(message, add_comment, user)


def add_comment(message, user):
    text = data.add_comment_db(message.text, user)
    if text == 'Комментарий добавлен.':
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(
            message.chat.id, 'Возникла ошибка. Попробуйте еще раз.')
        view_comment(message)


# keep_alive()
bot.polling(non_stop=True, interval=0)

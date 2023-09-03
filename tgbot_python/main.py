import os
# from background import keep_alive
import telebot
from telebot import types
import data
import config

bot = telebot.TeleBot(config.TOKEN_BOT)
id_city = None
id_hospital = None
id_pharmacy = None
id_drug = None
id_problems = None
clinic = []
message_back = {}


@bot.message_handler(commands=['start'])
def start(message):
    cites = data.get_cites()
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    for i in cites:
        keyword.add(types.KeyboardButton(i[1]))
    bot.send_message(message.chat.id, 'Выбери город', reply_markup=keyword)
    bot.register_next_step_handler(message, get_city, cites)


def get_city(message, cites):
    global id_city
    city = message.text
    for i in cites:
        if i[1].rstrip('\r') == city.rstrip('\r'):
            id_city = str(i[0])
            break
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    pharmacy_btn = types.KeyboardButton('Аптеки')
    hospital_btn = types.KeyboardButton('Поликлиники')
    keyword.add(pharmacy_btn, hospital_btn)
    bot.send_message(message.chat.id, 'Выбери метод', reply_markup=keyword)
    message_back['get_city'] = message
    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text.lower() == 'аптеки':
        pharmacy = data.get_pharmacies(id_city)
        keyword = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        for i in pharmacy:
            keyword.add(types.KeyboardButton(i[1]))
        bot.send_message(message.chat.id, 'Выбери аптеку',
                         reply_markup=keyword)
        bot.register_next_step_handler(
            message, choices_street_pharmacy, pharmacy)
    elif message.text.lower() == 'поликлиники':
        clinics = data.get_clinic(id_city)
        message_back['on_click'] = message
        bot.send_message(
            message.chat.id, 'Введи улицу на котой расположенна поликлиника:')
        bot.register_next_step_handler(message, choices_hospital, clinics)


def choices_street_pharmacy(message, pharma):
    street_pharmacy = []
    for i in pharma:
        if i[1].lower() == message.text.lower():
            street_pharmacy.append(i)
    bot.send_message(message.chat.id, 'Введите улицу, дом. Через пробел')
    bot.register_next_step_handler(message, view_drugs, street_pharmacy)


def view_drugs(message, street_home):
    global id_pharmacy
    street, home = message.text.lower().split()
    for i in street_home:
        if i[3].lower() == street and i[4].lower() == home:
            id_pharmacy = str(i[0])
            break
    drugs = data.get_drugs(id_pharmacy)
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    for i in drugs:
        keyword.add(types.KeyboardButton(i[1]))
    bot.send_message(message.chat.id, 'Выбери лекарство',
                     reply_markup=keyword)
    bot.register_next_step_handler(message, view_problem, drugs)


def view_problem(message, drugs):
    drug = message.text
    global id_drug
    id_problem = None
    text = ''
    for i in drugs:
        if i[1].lower() == drug.lower():
            id_drug = i[0]
            id_problem = i[3]
            break
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
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
        problems = data.view_problems()
        keyword = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        for el in problems:
            keyword.add(types.KeyboardButton(el[1].rstrip('\r')))
        bot.send_message(message.chat.id, 'Выбери', reply_markup=keyword)
        bot.register_next_step_handler(message, up_problem, problems)
    else:
        comments = data.get_comments(id_drug)
        text = ''
        keyword = types.ReplyKeyboardMarkup()
        if len(comments) == 0:
            text = 'Коментариев нет. Добавить?'
        else:
            len_comments = len(comments)
            if len_comments > 10:
                n = -10
            else:
                n = 0
            for el in range(n, len_comments):
                text += f'{comments[el][0]} от {comments[el][2]}: \n{comments[el][1]}\n'
        keyword.add(types.KeyboardButton('Добавить комментарий'),
                    types.KeyboardButton('В начало'))
        bot.send_message(message.chat.id, text, reply_markup=keyword)
        bot.register_next_step_handler(message, comment)


def comment(message):
    text = message.text
    if text.lower() == 'в начало':
        start(message)
    else:
        username = f'@{message.from_user.username}' if message.from_user.username else ''
        first_name = message.from_user.first_name if message.from_user.first_name else ''
        last_name = message.from_user.last_name if message.from_user.last_name else ''
        user = {
            'id_drug': id_drug,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
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
            message.chat.id, text)
        view_comment(message)


def up_problem(message, problems):
    text = message.text.lower()
    for i in problems:
        if i[1].rstrip('\r').lower() == text:
            bot.send_message(
                message.chat.id, data.update_problem(int(i[0]), id_drug))
            break


def choices_hospital(message, clinics):
    street = message.text.lower()
    message_back['choices_hospital'] = [message, clinics]
    clinic_on_street = []
    for i in clinics:
        if i[3].lower() == street:
            clinic_on_street.append(i)
    bot.send_message(message.chat.id, 'Введите дом:')
    bot.register_next_step_handler(
        message, choices_house_clinic, clinic_on_street)


def choices_house_clinic(message, clinics):
    house = message.text.lower()
    message_back['choices_house_clinic'] = [message, clinics]
    clinic = []
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    for i in clinics:
        if i[4].lower() == house:
            clinic.append(i)
            keyword.add(types.KeyboardButton(str(i[1])))
    bot.send_message(
        message.chat.id, 'Выбери лечебное учереждение:', reply_markup=keyword)
    bot.register_next_step_handler(message, view_drugs_on_clinic)


def view_drugs_on_clinic(message):
    text = message.text.lower()
    message_back['view_drugs_on_clinic'] = [message]
    global id_hospital
    appointment_id = 0
    clinic = message_back['choices_house_clinic'][1]
    for i in clinic:
        if text == i[1].lower():
            id_clinic = i[0]
            appointment_id = i[5]
            break
    drugs = data.get_drugs_in_clinic(id_clinic, appointment_id)
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    problem_drugs = set([i[1] for i in drugs if i[3] != 0])
    drugs = [i for i in drugs if i[3] != 0]
    if len(problem_drugs) == 0:
        bot.send_message(
            message.chat.id, 'Проблем с лекарствами нет. Молодцы!')
    else:
        for i in problem_drugs:
            keyword.add(types.KeyboardButton(i))
        bot.send_message(message.chat.id, 'Выбери лекарство:',
                         reply_markup=keyword)
        bot.register_next_step_handler(
            message, problem_and_comment, drugs)


def problem_and_comment(message, drugs):
    text = message.text.lower()
    message_back['problem_and_comment'] = [message, drugs]
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    keyword.add(types.KeyboardButton('Добавить комментарий'),
                types.KeyboardButton('Назад'))
    for i in drugs:
        if i[1].lower() == text:
            comment_clinic = data.get_comments(i[0])
            problem = data.get_problem(i[3])
            print(problem)
            if len(comment_clinic) == 0:
                bot.send_message(
                    message.chat.id, f'{i[1]}: {problem}\nКоментарии:\nКомментариев нет!', reply_markup=keyword)
                continue
            if len(comment_clinic) == 1:
                text_comment = comment_clinic[0]
                bot.send_message(
                    message.chat.id, f'{i[1]}: {problem}\nКоментарии:\n{text_comment}', reply_markup=keyword)
            else:
                text_comment = '\n'.join(comment_clinic[-2:len(comment)])
                bot.send_message(
                    message.chat.id, f'{i[1]}: {problem}\nКоментарии:\n{text_comment}', reply_markup=keyword)
    bot.register_next_step_handler(message, add_comment_for_clinic, drugs)


def add_comment_for_clinic(message, drugs):
    text = message.text.lower()
    if text == 'назад':
        view_drugs_on_clinic(message_back['view_drugs_on_clinic'])
    else:
        message_back['add_comment_for_clinic'] = [message, drugs]
        keyword = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        for i in drugs:
            problem = data.get_problem(i[3])
            keyword.add(types.KeyboardButton(f'{i[1]}: {problem}'))
        keyword.add(types.KeyboardButton('Назад'))
        bot.send_message(
            message.chat.id, 'выбери лекарство для каомментария:', reply_markup=keyword)
        bot.register_next_step_handler(message, update_comment_clinic, drugs)


def update_comment_clinic(message, drugs):
    text = message.text.lower()
    if text == 'назад':
        message_back.pop()
        problem_and_comment(*message_back['problem_and_comment'])
    else:
        text = text.split(': ')
        message_back['update_comment_clinic'] = [message, drugs]
        username = f'@{message.from_user.username}' if message.from_user.username else ''
        first_name = message.from_user.first_name if message.from_user.first_name else ''
        last_name = message.from_user.last_name if message.from_user.last_name else ''
        id_problem = data.get_id_problem(text[1])
        for i in drugs:
            if i[1] == text[0] and i[3] == id_problem:
                id_drug = i[0] 
        user = {
            'id_drug': id_drug,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }
        bot.send_message(
            message.chat.id, 'Напишите комментарий. Затем нажмите отправить.')
        bot.register_next_step_handler(message, add_comment_clinic, user)


def add_comment_clinic(message, user):
    text = data.add_comment_db(message.text, user)
    if text == 'Комментарий добавлен.':
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(
            message.chat.id, text)
    problem_and_comment(*message_back['problem_and_comment'])


# keep_alive()
bot.polling(non_stop=True, interval=0)

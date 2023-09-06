import os
# from background import keep_alive
import telebot
from telebot import types
import data
import config

bot = telebot.TeleBot(config.TOKEN_BOT)
ID_DRUG = None
message_back = {}


@bot.message_handler(commands=['start'])
def start(message):
    global message_back
    message_back = {}
    cites = data.get_cites()
    message_back['start'] = message
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    for i in cites:
        keyword.add(types.KeyboardButton(i[1]))
    bot.send_message(message.chat.id, 'Выбери город', reply_markup=keyword)
    bot.register_next_step_handler(message, get_city, cites)


def get_city(message, cites):
    city = message.text
    id_city = ''
    for i in cites:
        if i[1].rstrip('\r') == city.rstrip('\r'):
            id_city = str(i[0])
            break
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    pharmacy_btn = types.KeyboardButton('Аптеки')
    hospital_btn = types.KeyboardButton('Поликлиники')
    keyword.add(pharmacy_btn, hospital_btn)
    keyword.add(types.KeyboardButton('К выбору города'))
    bot.send_message(message.chat.id, 'Далее', reply_markup=keyword)
    message_back['get_city'] = message
    bot.register_next_step_handler(message, on_click, id_city)


def on_click(message, id_city):
    message_back['on_click'] = [message, id_city]
    if message.text.lower() == 'к выбору города':
        start(message)
    elif message.text.lower() == 'аптеки':
        pharmacy = data.get_pharmacies(id_city)
        bot.send_message(
            message.chat.id, 'Введите улицу:')
        bot.register_next_step_handler(
            message, choices_street_pharmacy, pharmacy)
    elif message.text.lower() == 'поликлиники':
        clinics = data.get_clinic(id_city)
        bot.send_message(
            message.chat.id, 'Введи улицу:')
        bot.register_next_step_handler(
            message, choices_street_clinic, clinics)


def choices_street_pharmacy(message, pharmacy):
    message_back['choices_street_pharmacy'] = [message, pharmacy]
    street_pharmacy = []
    for i in pharmacy:
        if i[3].lower() == message.text.lower():
            street_pharmacy.append(i)
    if len(street_pharmacy) == 0:
        bot.send_message(message.chat.id, 'Такой улицы нет. Попробуйте снова.')
        on_click(message_back['on_click'][0], message_back['on_click'][1])
    else:
        bot.send_message(message.chat.id, 'Введите дом:')
        bot.register_next_step_handler(
            message, choices_house_pharmacy, street_pharmacy)


def choices_house_pharmacy(message, street_pharmacy):
    """choices_house_pharmacy"""
    message_back['choices_house_pharmacy'] = [message, street_pharmacy]
    text = message.text.lower()
    pharmacy = []
    for i in street_pharmacy:
        if i[4].lower() == text:
            pharmacy.append(i)
    if len(pharmacy) == 0:
        bot.send_message(
            message.chat.id, 'В данном доме нет аптеки. Попробуйте снова.')
        choices_street_pharmacy(
            message_back['choices_street_pharmacy'][0], message_back['choices_street_pharmacy'][1])
    else:
        keyword = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        for i in pharmacy:
            keyword.add(types.KeyboardButton(i[1]))
        bot.send_message(message.chat.id, 'Выбери аптеку:',
                         reply_markup=keyword)
        bot.register_next_step_handler(message, view_drugs, pharmacy)


def view_drugs(message, pharmacy):
    """view drugs list"""
    message_back['view_drugs'] = [message, pharmacy]
    text = message.text.lower()
    id_pharmacy = 0
    for i in pharmacy:
        if text == i[1].lower:
            id_pharmacy = str(i[0])
            break
    drugs = data.get_drugs(id_pharmacy)
    keyword = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    for i in drugs:
        keyword.add(types.KeyboardButton(i[1]))
    keyword.add(types.KeyboardButton('Назад'))
    bot.send_message(message.chat.id, 'Выбери лекарство',
                     reply_markup=keyword)
    bot.register_next_step_handler(message, view_problem, drugs)


def view_problem(message, drugs):
    """view problem from drug"""
    message_back['view_problem'] = [message, drugs]
    drug = message.text.lower()
    if drug == 'назад':
        choices_street_pharmacy(
            message_back['choices_street_pharmacy'][0], message_back['choices_street_pharmacy'][1])
    else:
        global ID_DRUG
        id_problem = 0
        text = ''
        for i in drugs:
            if i[1].lower() == drug.lower():
                ID_DRUG = i[0]
                id_problem = i[3]
                break
        keyword = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        text = f'Проблема: {data.get_problem(id_problem)}. Обновить проблему?'
        keyword.add(types.KeyboardButton('Да'),
                    types.KeyboardButton('Посмотреть комментарии'))
        keyword.add(types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, text, reply_markup=keyword)
        bot.register_next_step_handler(message, view_comment)


def view_comment(message, flag=True):
    """view a comment on the drug"""
    text = message.text.lower()
    message_back['view_comment'] = message
    if text == 'назад':
        view_drugs(message_back['view_drugs'][0],
                   message_back['view_drugs'][1])
    elif text.lower() == 'да' and flag:
        problems = data.view_problems()
        keyword = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        for elem in problems:
            keyword.add(types.KeyboardButton(elem[1].rstrip('\r')))
        keyword.add(types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, 'Выбери', reply_markup=keyword)
        bot.register_next_step_handler(message, up_problem, problems)
    else:
        comments = data.get_comments(ID_DRUG)
        text = ''
        keyword = types.ReplyKeyboardMarkup()
        if len(comments) == 0:
            text = 'Коментариев нет. Добавить?'
        else:
            len_comments = len(comments)
            begin = -10 if len_comments > 10 else 0
            for i in range(begin, len_comments):
                text += f'{comments[i][0]} от {comments[i][2]}: \n{comments[i][1]}\n'
        if flag:
            keyword.add(types.KeyboardButton('Добавить комментарий'),
                    types.KeyboardButton('Назад'))
        else:
            keyword.add(types.KeyboardButton('В начало'), types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, text, reply_markup=keyword)
        bot.register_next_step_handler(message, comment)


def comment(message):
    """getting comment from user"""
    text = message.text
    if text.lower() == 'назад':
        view_problem(message_back['view_problem'][0],
                     message_back['view_problem'][1])
    elif text.lower() == 'добавить комментарий':
        username = f'@{message.from_user.username}' if message.from_user.username else ''
        first_name = message.from_user.first_name if message.from_user.first_name else ''
        last_name = message.from_user.last_name if message.from_user.last_name else ''
        user = {
            'id_drug': ID_DRUG,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }
        bot.send_message(
            message.chat.id, 'Напишите комментарий. Затем нажмите отправить.')
        bot.register_next_step_handler(message, add_comment, user)
    else:
        start(message_back['start'])

def add_comment(message, user):
    """added comment for drug"""
    text = data.add_comment_db(message.text, user)
    bot.send_message(
        message.chat.id, text)
    view_comment(message_back['view_comment'], flag=False)


def up_problem(message, problems):
    """update problem for drug"""
    text = message.text.lower()
    for i in problems:
        if i[1].rstrip('\r').lower() == text:
            keyword = types.ReplyKeyboardMarkup(
                one_time_keyboard=True, resize_keyboard=True)
            keyword.add(types.KeyboardButton('Добавить комментарий'))
            bot.send_message(
                message.chat.id, data.update_problem(int(i[0]), ID_DRUG), reply_markup=keyword)
            bot.register_next_step_handler(message, comment)


def choices_street_clinic(message, clinics):
    """choices_street_clinic"""
    street = message.text.lower()
    message_back['choices_street_clinic'] = [message, clinics]
    clinic_on_street = []
    for i in clinics:
        if i[3].lower() == street:
            clinic_on_street.append(i)
    if len(clinic_on_street) == 0:
        bot.send_message(
            message.chat.id, 'На этой улице нет поликлиники. Попробуйте ещё раз.')
        on_click(
            message_back['on_click'][0], message_back['on_click'][1])
    else:
        bot.send_message(message.chat.id, 'Введите дом:')
        bot.register_next_step_handler(
            message, choices_house_clinic, clinic_on_street)


def choices_house_clinic(message, clinics):
    """choices_house_clinic"""
    house = message.text.lower()
    message_back['choices_house_clinic'] = [message, clinics]
    clinic = []
    for i in clinics:
        if i[4].lower().rstrip('\r') == house:
            clinic.append(i)
    if len(clinic) == 0:
        bot.send_message(
            message.chat.id, 'В этом доме нет поликлиники. попробуйте еще раз.')
        choices_street_clinic(
            message_back['choices_street_clinic'][0], message_back['choices_street_clinic'][1])
    else:
        keyword = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        for i in clinic:
            keyword.add(types.KeyboardButton(str(i[1])))
        bot.send_message(
            message.chat.id, 'Выбери лечебное учереждение:', reply_markup=keyword)
        bot.register_next_step_handler(message, view_drugs_on_clinic, clinic)


def view_drugs_on_clinic(message, clinic):
    """view drugs from the clinic"""
    text = message.text.lower()
    message_back['view_drugs_on_clinic'] = [message, clinic]
    appointment_id = 0
    id_clinic = 0
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
        keyword.add(types.KeyboardButton('К выбору города'))
        bot.send_message(message.chat.id, 'Выбери лекарство:',
                         reply_markup=keyword)
        bot.register_next_step_handler(
            message, problem_and_comment, drugs)


def problem_and_comment(message, drugs):
    """view problem and comment"""
    text = message.text.lower()
    if text == 'к выбору города':
        start(message_back['start'])
    else:
        message_back['problem_and_comment'] = [message, drugs]
        keyword = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                            one_time_keyboard=True)
        keyword.add(types.KeyboardButton('Добавить комментарий'),
                    types.KeyboardButton('Назад'))
        for i in drugs:
            text_comment = ''
            if i[1].lower() == text:
                comment_clinic = data.get_comments(i[0])
                problem = data.get_problem(i[3])
                if len(comment_clinic) == 1:
                    text_comment = f'{comment_clinic[0][0]} от {comment_clinic[0][2]}: {comment_clinic[0][1]}\n'
                elif len(comment_clinic) > 1:
                    text_comment = f'{comment_clinic[-2][0]} от {comment_clinic[-2][2]}: {comment_clinic[-2][1]}\n'
                    text_comment += f'{comment_clinic[-1][0]} от {comment_clinic[-1][2]}: {comment_clinic[-1][1]}\n'
                else:
                    text_comment = 'Комментариев нет!'
                bot.send_message(message.chat.id,
                                 f'{i[1]}: {problem}\nКомментарии:\n{text_comment}',
                                 reply_markup=keyword)
        bot.register_next_step_handler(message, add_comment_for_clinic, drugs)


def add_comment_for_clinic(message, drugs):
    """choices drug for comment"""
    text = message.text.lower()
    if text == 'назад':
        view_drugs_on_clinic(
            message_back['view_drugs_on_clinic'][0], message_back['view_drugs_on_clinic'][1])
    else:
        message_back['add_comment_for_clinic'] = [message, drugs]
        keyword = types.ReplyKeyboardMarkup(
            one_time_keyboard=True, resize_keyboard=True)
        for i in drugs:
            problem = data.get_problem(i[3])
            keyword.add(types.KeyboardButton(f'{i[1]}: {problem}'))
        keyword.add(types.KeyboardButton('Назад'))
        bot.send_message(
            message.chat.id, 'выбери лекарство для комментария:', reply_markup=keyword)
        bot.register_next_step_handler(message, update_comment_clinic, drugs)


def update_comment_clinic(message, drugs):
    """getting comment from user"""
    text = message.text.lower()
    if text == 'назад':
        problem_and_comment(
            message_back['problem_and_comment'][0], message_back['problem_and_comment'][1])
    else:
        text = text.split(': ')
        message_back['update_comment_clinic'] = [message, drugs]
        username = f'@{message.from_user.username}' if message.from_user.username else ''
        first_name = message.from_user.first_name if message.from_user.first_name else ''
        last_name = message.from_user.last_name if message.from_user.last_name else ''
        id_problem = data.get_id_problem(text[1])
        id_drug = 0
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
    """added comment from the clinic"""
    text = data.add_comment_db(message.text, user)
    bot.send_message(
        message.chat.id, text)
    problem_and_comment(
        message_back['problem_and_comment'][0], message_back['problem_and_comment'][1])


# keep_alive()
bot.polling(non_stop=True, interval=0)

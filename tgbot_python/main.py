import os
import telebot
from telebot import types
import data
import config


class User_Bot():
    id_drug = None
    message_back = {}


def main():
    bot = telebot.TeleBot(config.TOKEN_BOT)
    user_bot = User_Bot()

    @bot.message_handler(commands=['start'])
    def start(message):
        # начало работы и получение списка городов
        cites = data.get_cites()
        user_bot.message_back['start'] = message
        keyword = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        for i in cites:
            keyword.add(types.KeyboardButton(i[1]))
        bot.send_message(message.chat.id, 'Выбери город', reply_markup=keyword)
        # with open('output.txt', 'w') as file:
        #    print(message, file=file)
        bot.register_next_step_handler(message, get_city, cites)

    def get_city(message, cites):
        city = message.text.lower()
        address = []
        for i in cites:
            if i[1].lower() == city:
                address.append(str(i[0]))
                break
        bot.send_message(message.chat.id, 'Введите улицу:')
        user_bot.message_back['get_city'] = [message, cites]
        bot.register_next_step_handler(message, choices_street, address)

    def choices_street(message, address):
        user_bot.message_back['choices_street'] = [message, address]
        if message.text.lower() == '/start':
            start(user_bot.message_back['start'])
        else:
            address.append(message.text.lower().title())
            structure = data.get_structure(address)
            if isinstance(structure, str):
                bot.send_message(message.chat.id, structure)
                get_city(*user_bot.message_back['get_city'])
            else:
                point_dict = {'pharmacy': [], 'clinic': []}
                for elem in structure:
                    if elem[1]:
                        value = data.get_pharmacies(elem[0])
                        if isinstance(value, str):
                            bot.send_message(message.chat.id, value)
                            start(user_bot.message_back['start'])
                        point_dict['pharmacy'] += value
                    if elem[2]:
                        value = data.get_clinic(elem[0])
                        if isinstance(value, str):
                            bot.send_message(message.chat.id, value)
                            start(user_bot.message_back['start'])
                        point_dict['clinic'] += value
                name_set = set()
                for val in point_dict.values():
                    for i in val:
                        if len(i) == 6:
                            house = data.get_house(i[4])
                        else:
                            house = data.get_house(i[3])
                        name_set.add(f'{i[1]}, дом: {house}')
                keyword = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, one_time_keyboard=True)
                keyword.add(*name_set)
                bot.send_message(message.chat.id, 'Выберите:',
                                 reply_markup=keyword)
                bot.register_next_step_handler(message, choices, point_dict)


    def choices(message, point_dict):
        """choices_house_pharmacy"""
        user_bot.message_back['choices'] = [
            message, point_dict]
        if message.text.lower() == '/start':
            start(user_bot.message_back['start'])
        else:
            text = message.text.split(', ')
            text = [text[0], *text[1].split()]
            your_flag = ''
            your_list = []
            for key, value in point_dict.items():
                for elem in value:
                    if len(elem) == 6:
                        house = data.get_house(elem[4])
                    else:
                        house = data.get_house(elem[3])
                    if text[0] == elem[1] and house == text[-1]:
                        your_flag = key
                        your_list = value
                        break
            if your_flag == 'pharmacy':
                drugs_pharmacy(message, your_list)
            elif your_flag == 'clinic':
                drugs_clinic(message, your_list)

    def drugs_pharmacy(message, your_list):
        user_bot.message_back['drugs_pharmacy'] = [message, your_list]
        drugs_list = []
        text = text = message.text.split(', ')
        for i in your_list:
            if text[0] == i[1]:
                drugs_list += data.get_drugs(i[0])
        drugs_name = set()
        for i in drugs_list:
            drugs_name.add(i[0][1])
        keyword = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        keyword.add(*drugs_name)
        keyword.add(types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, 'Выбери лекарство:',
                         reply_markup=keyword)
        bot.register_next_step_handler(message, view_problem, drugs_list)

    def view_problem(message, drugs):
        """view problem from drug"""
        user_bot.message_back['view_problem'] = [message, drugs]
        text = message.text.lower()
        if text == '/start':
            start(user_bot.message_back['start'])
        elif text == 'назад':
            get_city(user_bot.message_back['get_city']
                     [0], user_bot.message_back['get_city'][1])
        else:
            id_problem = 0
            for i in drugs:
                if i[0][1].lower() == text:
                    user_bot.id_drug = i[0][0]
                    id_problem = i[0][3]
                    break
            keyword = types.ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True)
            keyword.add(types.KeyboardButton('Обновить проблему'),
                        types.KeyboardButton('Посмотреть комментарии'))
            keyword.add(types.KeyboardButton('Назад'))
            bot.send_message(
                message.chat.id, f'Проблема: {data.get_problem(id_problem)}. Обновить проблему?', reply_markup=keyword)
            bot.register_next_step_handler(message, view_comment)

    def view_comment(message):
        """view a comment on the drug"""
        text = message.text.lower()
        user_bot.message_back['view_comment'] = message
        if text == '/start':
            start(user_bot.message_back['start'])
        elif text == 'назад':
            drugs_pharmacy(user_bot.message_back['drugs_pharmacy'][0],
                           user_bot.message_back['drugs_pharmacy'][1])
        elif text.lower() == 'обновить проблему':
            problems = data.view_problems()
            keyword = types.ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True)
            keyword.add(*[i[1] for i in problems])
            keyword.add(types.KeyboardButton('Назад'))
            bot.send_message(message.chat.id, 'Выбери', reply_markup=keyword)
            bot.register_next_step_handler(message, up_problem, problems)
        else:
            comments = data.get_comments(user_bot.id_drug)
            temp_text = ''
            keyword = types.ReplyKeyboardMarkup()
            if len(comments) == 0:
                temp_text = 'Коментариев нет. Добавить?'
            else:
                for i in range(len(comments) - 1, -1, -1):
                    temp_text = temp_text + \
                        f'{comments[i][0]} от {                     comments[i][2]}: \n{comments[i][1]}\n'
            keyword.add(types.KeyboardButton('Добавить комментарий'))
            keyword.add(types.KeyboardButton('В начало'),
                        types.KeyboardButton('Назад'))
            bot.send_message(message.chat.id, temp_text, reply_markup=keyword)
            bot.register_next_step_handler(message, comment)

    def comment(message):
        """getting comment from user"""
        text = message.text
        if text == '/start':
            start(user_bot.message_back['start'])
        elif text.lower() == 'назад':
            drugs_pharmacy(user_bot.message_back['drugs_pharmacy'][0],
                           user_bot.message_back['drugs_pharmacy'][1])
        elif text.lower() == 'добавить комментарий':
            username = f'@{message.from_user.username}' if message.from_user.username else ''
            first_name = message.from_user.first_name if message.from_user.first_name else ''
            last_name = message.from_user.last_name if message.from_user.last_name else ''
            user = {
                'id_drug': user_bot.id_drug,
                'username': username,
                'first_name': first_name,
                'last_name': last_name
            }
            bot.send_message(
                message.chat.id, 'Напишите комментарий. Затем нажмите отправить.')
            bot.register_next_step_handler(message, add_comment, user)
        else:
            start(user_bot.message_back['start'])

    def add_comment(message, user):
        """added comment for drug"""
        if message.text.lower() == '/start':
            start(user_bot.message_back['start'])
        elif message.text.lower() == 'назад':
            drugs_pharmacy(user_bot.message_back['drugs_pharmacy'][0],
                           user_bot.message_back['drugs_pharmacy'][1])
        text = data.add_comment_db(message.text, user)
        bot.send_message(
            message.chat.id, text)
        drugs_pharmacy(
            user_bot.message_back['drugs_pharmacy'][0], user_bot.message_back['drugs_pharmacy'][1])

    def up_problem(message, problems):
        """update problem for drug"""
        text = message.text.lower()
        if text == '/start':
            start(user_bot.message_back['start'])
        else:
            for i in problems:
                if i[1].rstrip('\r').lower() == text:
                    keyword = types.ReplyKeyboardMarkup(
                        one_time_keyboard=True, resize_keyboard=True)
                    keyword.add(types.KeyboardButton('Добавить комментарий'))
                    bot.send_message(
                        message.chat.id, data.update_problem(int(i[0]), user_bot.id_drug), reply_markup=keyword)
                    bot.register_next_step_handler(message, comment)

    def drugs_clinic(message, your_list):
        text = message.text.split(', ')[0]
        user_bot.message_back['drugs_clinic'] = [message, your_list]
        id_clinic = 0
        for i in your_list:
            if text == i[1]:
                id_clinic = i[0]
                break
        drugs = data.get_drugs_in_clinic(id_clinic)
        keyword = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)
        drugs = [i for i in drugs if i[3] != 0]
        problem_drugs = set([i[1] for i in drugs])
        if len(problem_drugs) == 0:
            bot.send_message(
                message.chat.id, 'Проблем с лекарствами нет. Молодцы!')
            start(user_bot.message_back['start'])
        else:
            keyword.add(*problem_drugs)
            keyword.add(types.KeyboardButton('К выбору города'))
            bot.send_message(message.chat.id, 'Выбери лекарство:',
                             reply_markup=keyword)
            bot.register_next_step_handler(
                message, problem_and_comment, drugs)

    def problem_and_comment(message, drugs):
        """view problem and comment"""
        text = message.text.lower()
        if text == '/start':
            start(user_bot.message_back['start'])
        elif text == 'к выбору города' or text == '/start':
            start(user_bot.message_back['start'])
        else:
            user_bot.message_back['problem_and_comment'] = [message, drugs]
            keyword = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                one_time_keyboard=True)
            keyword.add(types.KeyboardButton('Добавить комментарий'),
                        types.KeyboardButton('Назад'))
            for el in drugs:
                text_comment = ''
                if el[1].lower() == text:
                    comment_clinic = data.get_comments(el[0])
                    problem = data.get_problem(el[3])
                    text_comment = ''
                    if len(comment_clinic) == 0:
                        text_comment = 'Комментариев нет!'
                    else:
                        for i in range(len(comment_clinic) - 1, -1, -1):
                            text_comment = text_comment + \
                                f'{comment_clinic[i][0]} от {                                 comment_clinic[i][2]}: \n{comment_clinic[i][1]}\n'
                    bot.send_message(message.chat.id,
                                     f'{el[1]}: {problem}\nКомментарии: \n{                              text_comment}',
                                     reply_markup=keyword)
            bot.register_next_step_handler(
                message, add_comment_for_clinic, drugs)

    def add_comment_for_clinic(message, drugs):
        """choices drug for comment"""
        text = message.text.lower()
        if text == '/start':
            start(user_bot.message_back['start'])
        elif text == 'назад':
            drugs_clinic(
                user_bot.message_back['drugs_clinic'][0], user_bot.message_back['drugs_clinic'][1])
        else:
            user_bot.message_back['add_comment_for_clinic'] = [message, drugs]
            keyword = types.ReplyKeyboardMarkup(
                one_time_keyboard=True, resize_keyboard=True)
            for i in drugs:
                problem = data.get_problem(i[3])
                keyword.add(types.KeyboardButton(f'{i[0]}: {i[1]} {problem}'))
            keyword.add(types.KeyboardButton('Назад'))
            bot.send_message(
                message.chat.id, 'выбери лекарство для комментария:', reply_markup=keyword)
            bot.register_next_step_handler(
                message, update_comment_clinic, drugs)

    def update_comment_clinic(message, drugs):
        """getting comment from user"""
        text = message.text.lower()
        if text == '/start':
            start(user_bot.message_back['start'])
        elif text == 'назад':
            problem_and_comment(
                user_bot.message_back['problem_and_comment'][0], user_bot.message_back['problem_and_comment'][1])
        else:
            text = text.split(': ')
            user_bot.message_back['update_comment_clinic'] = [message, drugs]
            username = f'@{message.from_user.username}' if message.from_user.username else ''
            first_name = message.from_user.first_name if message.from_user.first_name else ''
            last_name = message.from_user.last_name if message.from_user.last_name else ''
            id_drug = text[0]
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
        if message.text.lower() == '/start':
            start(user_bot.message_back['start'])
        elif message.text.lower() == 'назад':
            drugs_clinic(
                user_bot.message_back['drugs_clinic'][0], user_bot.message_back['drugs_clinic'][1])
        text = data.add_comment_db(message.text, user)
        bot.send_message(
            message.chat.id, text)
        drugs_clinic(
            user_bot.message_back['drugs_clinic'][0], user_bot.message_back['drugs_clinic'][1])

    bot.polling(non_stop=True, interval=0)


if __name__ == '__main__':
    main()

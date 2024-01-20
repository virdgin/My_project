from aiogram.types import KeyboardButton, ReplyKeyboardMarkup



def keyboard(keywords, city=True) -> ReplyKeyboardMarkup:
    buttons = []
    temp = []
    for el in keywords:
        temp.append(KeyboardButton(text=el))
        if len(temp) == 3:
            buttons.append(temp)
            temp = []
    buttons.append(temp)
    if city:
        buttons.append([KeyboardButton(text='Назад')])
    keyword = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
    return keyword

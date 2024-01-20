from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.methods import send_message
import requests
import config
from app.main_router import choices, choices_street
from app import database
from keyboards.keyboard import keyboard
from app.form import Form, User


router = Router()


# @router.message(Form.CLINIC_DRUG, F.text == 'Назад')
# async def back_clinic(message: Message, state: FSMContext):
#    await state.set_state(Form.STREET)
#    await choices_street(User.data_message['choices_street'], state)


@router.message(Form.CLINIC_DRUG)
async def drugs_clinic(message: Message, state: FSMContext):
    data = await state.get_data()
    drugs = data['drugs']
    text = message.text.split(': ')
    comment_clinic = []
    problem = 0
    for el in drugs:
        text_comment = ''
        if int(el[0]) == int(text[0]):
            comment_clinic = database.get_comments(el[0])
            User.user['id_drug'] = el[0]
            problem = database.get_problem(el[3])
            break
    text_comment = ''
    if len(comment_clinic) == 0:
        text_comment = 'Комментариев нет!'
    else:
        for i in range(len(comment_clinic) - 1, -1, -1):
            text_comment = text_comment + \
                f'{comment_clinic[i][0]} от {comment_clinic[i][2]}:\n{comment_clinic[i][1]}\n'
    board = keyboard(['Добавить комментарий'])
    await state.set_state(Form.COMMENTS_C)
    await message.answer(f'{text[1]}: {problem}\nКомментрарии: {text_comment}', reply_markup=board)


@router.message(Form.COMMENTS_C, F.text == 'Добавить комментарий')
async def comments(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.ADD_COMMENT_C)
    await message.answer('Напишите комментарий. Затем нажмите отправить.')


@router.message(Form.ADD_COMMENT_C)
async def add_comment(message: Message, state: FSMContext) -> None:
    comment = f"{message.text}"
    reply_user = database.get_comments(User.user['id_drug'])
    if reply_user and reply_user[0][-1] != User.user['chat_id']:
        reply = database.reply_for_clinic(User.user['id_drug'])
        requests.get(f"https://api.telegram.org/bot{config.TOKEN_BOT}/sendMessage?chat_id={reply_user[0][-1]}&text={reply}")
        #send_message.SendMessage(chat_id=reply_user[0][-1], text=reply)
    await message.answer(database.add_comment_db(comment, User.user))
    await state.set_state(Form.HOUSE)
    await choices(User.data_message['choices'], state)


@router.message(F.text == 'Назад')
async def back_drug_clinic(message: Message, state: FSMContext):
    await state.set_state(Form.HOUSE)
    await choices(User.data_message['choices'], state)

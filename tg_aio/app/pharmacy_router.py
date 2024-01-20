from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.methods import send_message
import requests
import config
from app.main_router import choices, choices_street, pharmacy
from app import database
from keyboards.keyboard import keyboard
from app.form import Form, User


router = Router()


#@router.message(Form.PHARMACY_DRUG, F.text == 'Назад')
#async def back_pharmacy(message: Message, state: FSMContext):
#    await state.set_state(Form.STREET)
#    await choices_street(User.data_message['choices_street'], state)


@router.message(Form.PHARMACY_DRUG)
async def drug_pharmacy(message: Message, state: FSMContext):
    await state.set_state(Form.PROBLEM)
    drug = await state.get_data()
    drug_list = drug['drugs']
    id_problem = 0
    for i in drug_list:
        if i[1].lower() == message.text.lower():
            User.user['id_drug'] = i[0]
            id_problem = i[3]
            break
    board = keyboard(['Обновить проблему', 'Посмотреть комментарии'])
    await message.answer(f'Проблема: {database.get_problem(id_problem)}.', reply_markup=board)


@router.message(Form.PROBLEM, F.text == 'Обновить проблему')
async def problem(message: Message, state: FSMContext):
    problems = database.view_problems()
    board = keyboard([i[1] for i in problems])
    await state.set_state(Form.UP_PROBLEM)
    await message.answer('Выбери проблему', reply_markup=board)


@router.message(Form.UP_PROBLEM)
async def up_problem(message: Message, state: FSMContext):
    id_problem = database.get_id_problem(message.text.lower())
    await message.answer(database.update_problem(id_problem, User.user['id_drug']))
    await state.set_state(Form.HOUSE)
    await choices(User.data_message['choices'], state)
    


@router.message(Form.PROBLEM, F.text == 'Посмотреть комментарии')
async def view_comments(message: Message, state: FSMContext) -> None:
    comments = database.get_comments(User.user['id_drug'])
    temp_text = ''
    if len(comments) == 0:
        temp_text = 'Коментариев нет. Добавить?'
    else:
        for i in range(len(comments) - 1, -1, -1):
            temp_text = temp_text + \
                f'{comments[i][0]} от {comments[i][2]}: \n{comments[i][1]}\n'
    board = keyboard(['Добавить комментарий'])
    await state.set_state(Form.COMMENTS_PH)
    await message.answer(temp_text, reply_markup=board)


@router.message(Form.COMMENTS_PH, F.text == 'Добавить комментарий')
async def comments(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.ADD_COMMENT_PH)
    await message.answer('Напишите комментарий. Затем нажмите отправить.')

@router.message(Form.ADD_COMMENT_PH)
async def add_comment(message: Message, state: FSMContext)-> None:
    data = await state.get_data()
    comment = f"{message.text}\n{data['pharmacy']}, {data['chosen_street']} {data['house']}"
    reply_user = database.get_comments(User.user['id_drug'])
    if reply_user and reply_user[0][-1] != User.user['chat_id']:
        reply = database.reply_for_pharmacy(User.user['id_drug'])
        requests.get(f"https://api.telegram.org/bot{config.TOKEN_BOT}/sendMessage?chat_id={reply_user[0][-1]}&text={reply}")
        #send_message.SendMessage(chat_id=reply_user[-1][-1], text=reply)
    await message.answer(database.add_comment_db(comment, User.user))
    await state.set_state(Form.HOUSE)
    await choices(User.data_message['choices'], state)

@router.message(F.text == 'Назад')
async def back_drug_pharmacy(message: Message, state: FSMContext):
    await state.set_state(Form.HOUSE)
    await choices(User.data_message['choices'], state)

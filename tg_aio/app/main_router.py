from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app import database
from keyboards.keyboard import keyboard
from app.form import Form, User


router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    User.list_cites = database.get_cites()
    board = keyboard(User.list_cites, False)
    User.user['user_id'] = message.from_user.id
    User.user['first_name'] = message.from_user.first_name if message.from_user.first_name else ''
    User.user['last_name'] = message.from_user.last_name if message.from_user.last_name else ''
    User.user['username'] = f'@{message.from_user.username}' if message.from_user.username else ''
    User.user['chat_id'] = message.chat.id
    await state.set_state(Form.CITY)
    await message.answer('Выбери город:', reply_markup=board)


@router.message(Form.CITY, lambda query: query.text not in User.list_cites)
async def error_city(message: Message, state: FSMContext) -> None:
    await message.answer('Такого города нет.')
    await state.clear()
    await start(message, state)


@router.message(Form.CITY, lambda query: query.text in User.list_cites)
async def get_city(message: Message, state: FSMContext) -> None:
    await state.update_data(chosen_city=message.text)
    await state.set_state(Form.STREET)
    User.data_message['get_city'] = message
    await message.answer('Введите улицу:')


@router.message(Form.STREET)
async def choices_street(message: Message, state: FSMContext):
    await state.update_data(chosen_street=message.text.lower().title())
    address = await state.get_data()
    structure = database.get_structure(
        [address['chosen_city'], address['chosen_street']])
    if isinstance(structure, str):
        await message.answer(structure)
        await state.set_state(Form.CITY)
        await get_city(User.data_message['get_city'], state)
    else:
        User.data_message['choices_street'] = message
        User.name_set.clear()
        User.point_dict['pharmacy'].clear()
        User.point_dict['clinic'].clear()
        for elem in structure:
            if elem[1]:
                value = database.get_pharmacies(elem[0])
                if isinstance(value, str):
                    await message.answer(value)
                    start(message, state)
                User.point_dict['pharmacy'] += value
            if elem[2]:
                value = database.get_clinic(elem[0])
                if isinstance(value, str):
                    await message.answer(value)
                    start(message, state)
                User.point_dict['clinic'] += value
        for val in User.point_dict.values():
            for i in val:
                house = database.get_house(i[1])
                User.name_set.add(f'{i[2]}, дом: {house}')
        board = keyboard(User.name_set)
        await state.set_state(Form.HOUSE)
        await message.answer('Выберите:', reply_markup=board)


@router.message(Form.HOUSE, F.text == 'Назад')
@router.message(Form.HOUSE, lambda message: message.text in User.name_set)
async def choices(message: Message, state: FSMContext):
    if message.text == 'Назад':
        await state.set_state(Form.CITY)
        await get_city(User.data_message['get_city'], state)
    else:
        User.data_message['choices'] = message
        text = message.text.split(', ')
        await state.update_data(house=text[1])
        text = [text[0], *text[1].split()]
        your_flag = ''
        your_list = []
        for key, value in User.point_dict.items():
            for elem in value:
                house = database.get_house(elem[1])
                if text[0] == elem[2] and house == text[-1]:
                    your_flag = key
                    your_list = value
                    break
        if your_flag == 'pharmacy':
            await pharmacy(message, your_list, state)
        elif your_flag == 'clinic':
            await clinic(message, your_list, state)


async def pharmacy(message, your_list, state):
    User.data_message['pharmacy'] = [message, your_list]
    drugs_list = []
    text = message.text.split(', ')
    await state.update_data(pharmacy=text[0])
    for i in your_list:
        if text[0] == i[2]:
            drugs_list += database.get_drugs(i[0])
    drugs_set = set(drugs_list)
    await state.update_data(drugs=drugs_set)
    board = keyboard([i[1] for i in drugs_set])
    await state.set_state(Form.PHARMACY_DRUG)
    await message.answer('Выберите лекарство:', reply_markup=board)


async def clinic(message, your_list, state):
    text = message.text.split(', ')[0]
    User.data_message['drugs_clinic'] = [message, your_list]
    id_clinic = 0
    for i in your_list:
        if text == i[2]:
            id_clinic = i[0]
            break
    drugs = database.get_drugs_in_clinic(id_clinic)
    drugs = [i for i in drugs if i[3] != 0]
    await state.update_data(drugs=drugs)
    problem_drugs = [f'{i[0]}: {i[1]}' for i in drugs]
    if len(problem_drugs) == 0:
        await message.answer('Проблем с лекарствами нет. Молодцы!')
        await state.clear()
        await start(message, state)
    else:
        board = keyboard(problem_drugs)
        await state.set_state(Form.CLINIC_DRUG)
        await message.answer('Выберите лекарство:', reply_markup=board)


@router.message(Form.CLINIC_DRUG, F.text == 'Назад')
@router.message(Form.PHARMACY_DRUG, F.text == 'Назад')
async def back_pharmacy(message: Message, state: FSMContext):
    await state.set_state(Form.STREET)
    await choices_street(User.data_message['choices_street'], state)

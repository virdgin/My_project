from aiogram.fsm.state import State, StatesGroup



class Form(StatesGroup):
    CITY = State()
    STREET = State()
    HOUSE = State()
    PHARMACY_DRUG = State()
    CLINIC_DRUG = State()
    PROBLEM = State()
    UP_PROBLEM = State()
    COMMENTS_PH =State()
    COMMENTS_C =State()
    ADD_COMMENT_PH = State()
    ADD_COMMENT_C =State()
    
class User():
    user = {}
    list_cites = []
    data_message = {}
    point_dict = {'pharmacy': [], 'clinic': []}
    name_set = set()
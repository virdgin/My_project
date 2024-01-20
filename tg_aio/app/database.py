'''module for work with bd'''
import sqlite3
from datetime import datetime, timedelta
import os
FILENAME = "/data/table.wife" if "AMVERA" in os.environ else "data/table.wife"


def get_cites():
    """getting a list cities"""
    table = sqlite3.connect(FILENAME)
    cursor = table.cursor()
    cites = []
    for i in cursor.execute("SELECT name FROM 'cites'"):
        cites.append(i[0].strip())
    cursor.close()
    table.close()
    return cites


def get_structure(address):
    try:
        table = sqlite3.connect(FILENAME)
        cur = table.cursor()
        city_id = cur.execute('SELECT id FROM cites WHERE name=:city', {'city': address[0]}).fetchall()[0][0]
        structure = []
        for i in cur.execute("SELECT id, pharmacy, clinic, house FROM address WHERE cities_id=:city_id AND street=:street;", {'city_id': city_id, 'street': address[1]}):
            structure.append(i)
    except sqlite3.Error:
        return 'Произошла ошибка.\n Попробуйте позднее, либо обратитесь в службу поддержки.'
    else:
        if len(structure) == 0:
            return 'По этому адресу ничего нет, попробуйте снова.'
        return structure
    finally:
        cur.close()
        table.close()


def get_pharmacies(id_address):
    try:
        table = sqlite3.connect(FILENAME)
        cur = table.cursor()
        pharmacy_list = []
        for i in cur.execute("SELECT * FROM pharmacies WHERE address_id=:id_address;", {'id_address': id_address}):
            pharmacy_list.append(i)
    except sqlite3.Error:
        return 'Произошла ошибка.\n Попробуйте позднее, либо обратитесь в службу поддержки.'
    else:
        return pharmacy_list
    finally:
        cur.close()
        table.close()


def get_house(id_address):
    try:
        table = sqlite3.connect(FILENAME)
        cur = table.cursor()
        house = cur.execute("SELECT house FROM address WHERE id=:id_address;", {
                            'id_address': id_address}).fetchall()
    except sqlite3.Error:
        return 'Произошла ошибка.\n Попробуйте позднее, либо обратитесь в службу поддержки.'
    else:
        return house[0][0]
    finally:
        cur.close()
        table.close()


def get_clinic(id_address):
    try:
        table = sqlite3.connect(FILENAME)
        cur = table.cursor()
        pharmacy_list = []
        for i in cur.execute("SELECT * FROM clinics WHERE address_id=:id_address;", {'id_address': id_address}):
            pharmacy_list.append(i)
    except sqlite3.Error:
        return 'Произошла ошибка.\n Попробуйте позднее, либо обратитесь в службу поддержки.'
    else:
        return pharmacy_list
    finally:
        cur.close()
        table.close()


def get_drugs(pharmacy):
    """getting a list of drugs in the pharmacy"""
    table = sqlite3.connect(FILENAME)
    cur = table.cursor()
    drugs_list = []
    temp_drugs = []
    for i in cur.execute("SELECT drugs_id FROM conn_d_ph WHERE pharmacy_id=:id_pharmacy;", {'id_pharmacy': pharmacy}):
        temp_drugs.append(i[0])
    req = "SELECT DISTINCT * FROM drugs WHERE id="
    for i in temp_drugs:
        drugs_list += cur.execute(req + str(i)).fetchall()
    cur.close()
    table.close()
    return set(drugs_list)


def get_problem(id_problem):
    """getting problem information"""
    table = sqlite3.connect(FILENAME)
    cur = table.cursor()
    problem = cur.execute("SELECT name FROM problems WHERE id=:id_problem;", {
                          'id_problem': id_problem}).fetchall()
    cur.close()
    table.close()
    return problem[0][0]

def get_comments(id_drug):
    """getting comment information"""
    table = sqlite3.connect(FILENAME)
    cur = table.cursor()
    comments = []
    for i in cur.execute("SELECT  date, descriptions, user_name, user_id FROM comments WHERE drugs_id=:id_drug ORDER BY id DESC LIMIT 5;", {'id_drug': id_drug}):
        comments.append(i)
    cur.close()
    table.close()
    return comments


def add_comment_db(message, user):
    """insert comment in database"""
    try:
        time = datetime.now() + timedelta(hours=3)
        time = time.strftime('%d.%m.%Y %H:%M')
        table = sqlite3.connect(FILENAME)
        cur = table.cursor()
        cur.execute("INSERT INTO comments (date, descriptions, drugs_id, user_name, user_id)VALUES(?,?,?,?,?)",
                    (time, message, user['id_drug'], f"{user['first_name']} {user['username']} {user['last_name']}", user['chat_id']))
        table.commit()
    except sqlite3.Error:
        return 'Произошла ошибка.\n Попробуйте позднее.'
    else:
        return 'Комментрий добавлен.'
    finally:
        cur.close()
        table.close()


def view_problems():
    """view all problems"""
    table = sqlite3.connect(FILENAME)
    cur = table.cursor()
    problems = cur.execute("SELECT id, name FROM problems;").fetchall()
    cur.close()
    table.close()
    return problems


def update_problem(id_problem, drug):
    """update problem for drug"""
    try:
        table = sqlite3.connect(FILENAME)
        cursor = table.cursor()
        data_request = "UPDATE drugs SET problem_id = ? WHERE id = ?"
        cursor.execute(data_request, (id_problem, drug))
        table.commit()
    except sqlite3.Error:
        return 'Произошла ошибка.\n Попробуйте позднее.'
    else:
        return 'Проблема обновленна.'
    finally:
        cursor.close()
        table.close()


def get_drugs_in_clinic(id_clinic):
    """getting drugs of clinic"""
    table = sqlite3.connect(FILENAME)
    cursor = table.cursor()
    data_request = "SELECT id FROM pharmacies WHERE clinic_id=" + \
        str(id_clinic)
    pharmacy = []
    for el in cursor.execute(data_request):
        pharmacy.append(el[0])
    drugs = []
    for i in pharmacy:
        request = "SELECT drugs_id FROM conn_d_ph WHERE pharmacy_id=" + str(i)
        drugs += cursor.execute(request).fetchall()
    drugs_list = []
    for el in drugs:
        data_request = "SELECT * FROM drugs WHERE id=" + str(el[0])
        drugs_list += cursor.execute(data_request).fetchall()
    cursor.close()
    table.close()
    return set(drugs_list)


def get_id_problem(name_problem):
    """getting id problem by name"""
    table = sqlite3.connect(FILENAME)
    cursor = table.cursor()
    problem_id = cursor.execute("SELECT id FROM problems WHERE name=:name_problem", {
        'name_problem': f'{name_problem}'}).fetchall()
    cursor.close()
    table.close()
    return (int(problem_id[0][0]))


def reply_for_pharmacy(id_drug):
    try:
        table = sqlite3.connect(FILENAME)
        cursor = table.cursor()
        reply = {}
        data_request = "SELECT pharmacy_id FROM conn_d_ph WHERE drugs_id=" + \
            str(id_drug)
        pharmacy_id = cursor.execute(data_request).fetchall()[0][0]
        data_request = "SELECT clinic_id FROM pharmacies WHERE id=" + \
            str(pharmacy_id)
        clinic_id = cursor.execute(data_request).fetchall()[0][0]
        data_request = "SELECT name, address_id FROM clinics WHERE id=" + \
            str(clinic_id)
        clinic = cursor.execute(data_request).fetchall()
        reply['clinic'] = (clinic[0][0])
        data_request = "SELECT name, problem_id FROM drugs WHERE id=" + \
            str(id_drug)
        drug = cursor.execute(data_request).fetchall()
        reply['drug'] = drug[0][0]
        data_request = "SELECT name FROM problems WHERE id=" + str(drug[0][1])
        problem = cursor.execute(data_request).fetchall()[0][0]
        reply['problem'] = problem
        data_request = "SELECT street, house FROM address WHERE id=" + \
            str(clinic[0][1])
        address = cursor.execute(data_request).fetchall()
        reply['address'] = f"{address[0][0]}, {address[0][1]}"
        text_reply = f"Новый комментарий\nКлиника: {reply['clinic']}\nАдрес: {reply['address']}\nЛекарство: {reply['drug']}\nПроблема: {reply['problem']}"
    except sqlite3.Error:
        return 'Произошла ошибка.\n Попробуйте позднее.'
    else:
        return text_reply
    finally:
        cursor.close()
        table.close()


def reply_for_clinic(id_drug):
    try:
        table = sqlite3.connect(FILENAME)
        cursor = table.cursor()
        reply = {}
        data_request = "SELECT pharmacy_id FROM conn_d_ph WHERE drugs_id=" + \
            str(id_drug)
        pharmacy_id = cursor.execute(data_request).fetchall()[0][0]
        data_request = "SELECT name, address_id FROM pharmacies WHERE id=" + \
            str(pharmacy_id)
        pharmacy = cursor.execute(data_request).fetchall()
        reply['pharmacy'] = pharmacy[0][0]
        data_request = "SELECT name, problem_id FROM drugs WHERE id=" + \
            str(id_drug)
        drug = cursor.execute(data_request).fetchall()
        reply['drug'] = drug[0][0]
        data_request = "SELECT name FROM problems WHERE id=" + str(drug[0][1])
        problem = cursor.execute(data_request).fetchall()[0][0]
        reply['problem'] = problem
        data_request = "SELECT street, house FROM address WHERE id=" + \
            str(pharmacy[0][1])
        address = cursor.execute(data_request).fetchall()
        reply['address'] = f"{address[0][0]}, {address[0][1]}"
        text_reply = f"Новый комментарий\nАптека: {reply['pharmacy']}\nАдрес: {reply['address']}\nЛекарство: {reply['drug']}\nПроблема: {reply['problem']}"
    except sqlite3.Error:
        return 'Произошла ошибка.\n Попробуйте позднее.'
    else:
        return text_reply
    finally:
        cursor.close()
        table.close()

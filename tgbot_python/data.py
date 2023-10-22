'''module for work with bd'''
import sqlite3
from datetime import datetime, timedelta


def get_cites():
    """getting a list cities"""
    table = sqlite3.connect('table.wife')
    cur = table.cursor()
    cites = []
    for i in cur.execute("SELECT id, name FROM cites;"):
        cites.append(i)
    cur.close()
    table.close()
    return cites


def get_structure(address):
    try:
        table = sqlite3.connect('table.wife')
        cur = table.cursor()
        structure = []
        for i in cur.execute("SELECT id, pharmacy, clinic, house FROM address WHERE cities_id=:city_id AND street=:street;", {'city_id': address[0], 'street': address[1]}):
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
        table = sqlite3.connect('table.wife')
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
        table = sqlite3.connect('table.wife')
        cur = table.cursor()
        house = cur.execute("SELECT house FROM address WHERE id=:id_address;", {'id_address': id_address}).fetchall()
    except sqlite3.Error:
        return 'Произошла ошибка.\n Попробуйте позднее, либо обратитесь в службу поддержки.'
    else:
        return house[0][0]
    finally:
        cur.close()
        table.close()

def get_clinic(id_address):
    try:
        table = sqlite3.connect('table.wife')
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
    table = sqlite3.connect('table.wife')
    cur = table.cursor()
    drugs_list = []
    temp_drugs = []
    for i in cur.execute("SELECT drugs_id FROM conn_d_ph WHERE pharmacy_id=:id_pharmacy;", {'id_pharmacy': pharmacy}):
        temp_drugs.append(i)
    req = "SELECT DISTINCT * FROM drugs WHERE id="
    for i in temp_drugs:
        drugs_list.append(cur.execute(req + str(i[0])).fetchall())
    cur.close()
    table.close()
    return drugs_list


def get_problem(id_problem):
    """getting problem information"""
    table = sqlite3.connect('table.wife')
    cur = table.cursor()
    problem = cur.execute("SELECT name FROM problems WHERE id=:id_problem;", {
                          'id_problem': id_problem}).fetchall()
    cur.close()
    table.close()
    return problem[0][0]


def get_comments(id_drug):
    """getting comment information"""
    table = sqlite3.connect('table.wife')
    cur = table.cursor()
    comments = []
    for i in cur.execute("SELECT  date, descriptions, user_name FROM comments WHERE drugs_id=:id_drug ORDER BY id DESC LIMIT 5;", {'id_drug': id_drug}):
        comments.append(i)
    cur.close()
    table.close()
    return comments


def add_comment_db(message, user):
    """insert comment in database"""
    try:
        time = datetime.now()
        time = time.strftime('%d.%m.%Y %H:%M')
        table = sqlite3.connect('table.wife')
        cur = table.cursor()
        cur.execute("INSERT INTO comments (date, descriptions, drugs_id, user_name)VALUES(?,?,?,?)",
                    (time, message, user['id_drug'], f"{user['first_name']} {user['username']} {user['last_name']}"))
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
    table = sqlite3.connect('table.wife')
    cur = table.cursor()
    problems = cur.execute("SELECT id, name FROM problems;").fetchall()
    cur.close()
    table.close()
    return problems


def update_problem(id_problem, drug):
    """update problem for drug"""
    try:
        table = sqlite3.connect('table.wife')
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
    table = sqlite3.connect('table.wife')
    cursor = table.cursor()
    data_request = "SELECT id FROM pharmacies WHERE clinic_id=" + str(id_clinic)
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
    return drugs_list


def get_id_problem(name_problem):
    """getting id problem by name"""
    table = sqlite3.connect('table.wife')
    cursor = table.cursor()
    problem_id = cursor.execute("SELECT id FROM problems WHERE name=:name_problem", {
        'name_problem': f'{name_problem}'}).fetchall()
    cursor.close()
    table.close()
    return (int(problem_id[0][0]))


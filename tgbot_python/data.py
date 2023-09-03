'''module for work with bd'''
import sqlite3
from datetime import datetime


def get_cites():
    """getting a list cities"""
    table = sqlite3.connect('table.db')
    cur = table.cursor()
    cites = []
    for i in cur.execute("SELECT id, name FROM cites;"):
        cites.append(i)
    cur.close()
    table.close()
    return cites


def get_pharmacies(id_city):
    """getting a list of pharmacies in the city"""
    table = sqlite3.connect('table.db')
    cur = table.cursor()
    pharmacy_list = []
    for i in cur.execute("SELECT * FROM pharmacies WHERE city_id=:id_city;", {'id_city': id_city}):
        pharmacy_list.append(i)
    cur.close()
    table.close()
    return pharmacy_list


def get_clinic(id_city):
    """getting a list of clinics in the city"""
    table = sqlite3.connect('table.db')
    cur = table.cursor()
    clinics_list = []
    for i in cur.execute("SELECT * FROM clinics WHERE city_id=:id_city;", {'id_city': id_city}):
        clinics_list.append(i)
    cur.close()
    table.close()
    return clinics_list


def get_drugs(id_pharmacy):
    """getting a list of drugs in the pharmacy"""
    table = sqlite3.connect('table.db')
    cur = table.cursor()
    drugs_list = []
    for i in cur.execute("SELECT * FROM drugs WHERE pharmacy_id=:id_pharmacy;", {'id_pharmacy': id_pharmacy}):
        drugs_list.append(i)
    cur.close()
    table.close()
    return drugs_list


def get_problem(id_problem):
    """getting problem information"""
    table = sqlite3.connect('table.db')
    cur = table.cursor()
    problem = cur.execute("SELECT name FROM problems WHERE id=:id_problem;", {
                          'id_problem': id_problem}).fetchall()
    cur.close()
    table.close()
    return problem[0][0].strip('\r')


def get_comments(id_drug):
    """getting comment information"""
    table = sqlite3.connect('table.db')
    cur = table.cursor()
    comments = []
    for i in cur.execute("SELECT date, descriptions, user_name FROM comments WHERE drugs_id=:id_drug", {'id_drug': id_drug}):
        comments.append(i)
    cur.close()
    table.close()
    return comments


def add_comment_db(message, user):
    """insert comment in database"""
    try:
        time = datetime.now().strftime('%d.%m.%Y %H:%M')
        table = sqlite3.connect('table.db')
        cur = table.cursor()
        cur.execute("INSERT INTO comments (date, descriptions, drugs_id, user_name)VALUES(?,?,?,?)",
                    (time, message, user['id_drug'], f"{user['first_name']} {user['username']} {user['last_name']}"))
        table.commit()
    except sqlite3.Error:
        return f'Произошла ошибка.\n Попробуйте позднее.'
    else:
        return 'Комментрий добавлен.'
    finally:
        cur.close()
        table.close()

def view_problems():
    """view all problems"""
    table = sqlite3.connect('table.db')
    cur = table.cursor()
    problems = cur.execute("SELECT id, name FROM problems;").fetchall()
    cur.close()
    table.close()
    return problems

def update_problem(id_problem, drug):
    """update problem for drug"""
    try:
        table =sqlite3.connect('table.db')
        cur = table.cursor()
        data_request = "UPDATE drugs SET problem_id = ? WHERE id = ?"
        cur.execute(data_request, (id_problem,drug))
        table.commit()
    except sqlite3.Error:
        return f'Произошла ошибка.\n Попробуйте позднее.'
    else:
        return 'Проблема обновленна.'
    finally:
        cur.close()
        table.close()

def get_drugs_in_clinic(id_clinic, appointment_id):
    """getting drugs of clinic"""
    table = sqlite3.connect('table.db')
    cursor = table.cursor()
    data_request = "SELECT id FROM pharmacies WHERE hospital_id=" + str(id_clinic)
    pharma = []
    for el in cursor.execute(data_request):
        pharma.append(el[0])
    drugs = []
    for i in pharma:
        drugs += cursor.execute("SELECT * FROM drugs WHERE pharmacy_id=" + str(i)).fetchall()
    drugs = [i for i in drugs if i[4] == appointment_id]
    cursor.close()
    table.close()
    return drugs

def get_id_problem(name_problem):
    table = sqlite3.connect('table.db')
    cursor = table.cursor()
    name = cursor.execute("SELECT id FROM problems WHERE name=:name_problem", {'name_problem': f'{name_problem}\r'}).fetchall()
    cursor.close()
    table.close()
    return (int(name[0][0]))


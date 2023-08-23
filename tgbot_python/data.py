'''module for work with bd'''
import sqlite3
from datetime import datetime


def get_cites():
    """getting a list cities"""
    table = sqlite3.connect('table.sql')
    cur = table.cursor()
    cites = []
    for i in cur.execute("SELECT id, name FROM cites;"):
        cites.append(i)
    cur.close()
    table.close()
    return cites


def get_pharmacies(id_city):
    """getting a list of pharmacies in the city"""
    table = sqlite3.connect('table.sql')
    cur = table.cursor()
    pharmacy_list = []
    for i in cur.execute("SELECT * FROM pharmacies WHERE city_id=:id_city;", {'id_city': id_city}):
        pharmacy_list.append(i)
    cur.close()
    table.close()
    return pharmacy_list


def get_clinic(id_city):
    """getting a list of clinics in the city"""
    table = sqlite3.connect('table.sql')
    cur = table.cursor()
    clinics_list = []
    for i in cur.execute("SELECT * FROM clinics WHERE city_id=:id_city;", {'id_city': id_city}):
        clinics_list.append(i)
    cur.close()
    table.close()
    return clinics_list


def get_drugs(id_pharmacy):
    """getting a list of drugs in the pharmacy"""
    table = sqlite3.connect('table.sql')
    cur = table.cursor()
    drugs_list = []
    for i in cur.execute("SELECT * FROM drugs WHERE pharmacy_id=:id_pharmacy;", {'id_pharmacy': id_pharmacy}):
        drugs_list.append(i)
    cur.close()
    table.close()
    return drugs_list


def get_problem(id_problem):
    """getting problem information"""
    table = sqlite3.connect('table.sql')
    cur = table.cursor()
    problem = cur.execute("SELECT name FROM problems WHERE id=:id_problem;", {
                          'id_problem': id_problem})
    cur.close()
    table.close()
    return problem.strip()


def get_comments(id_drug):
    """getting comment information"""
    table = sqlite3.connect('table.sql')
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
        table = sqlite3.connect('table.sql')
        cur = table.cursor()
        cur.execute("INSERT INTO comments VALUES(?,?,?,?)",(time, message, user['id_drug'], f"{user['first_name']} {user['username']} {user['last_name']}"))
        table.commit()
        cur.close()
        table.close()
    except:
        cur.close()
        table.close()
        return False
        
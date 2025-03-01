from flask import request, current_app, g
from dotenv import load_dotenv
from .dbconnect import get_db

def insert_data():
    print("in insert data")
    if request.method == 'POST':
        db = get_db()
        print("request method post")
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        reg_user = {}
        reg_user['name'] = name
        reg_user['email'] = email
        reg_user['password'] = password

        users = db['user']
        if users.find_one({"email":email}) == None:
            users.insert_one(reg_user)
            return True
        else:
            return False


def check_user():
    if request.method == 'POST':
        print("in check_user")
        db = get_db()
        users = db['user']
        email = request.form['email']
        password = request.form['password']

        login_user = {
            "email": email,
            "password": password
        }

        print(email)
        print(password)
        user_data = users.find_one(login_user)
        if user_data == None:
            print("user not found")
            return False, ""
        else:
            print("user found")
            return True, user_data["name"]

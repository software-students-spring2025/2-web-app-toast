from flask import Blueprint, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from .userdb import insert_data, check_user
'''
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    print("in login post")
    [flag, username] = check_user()

    if(flag):
        print(username + "logged in")
        return 'login success'
    else:
        return redirect(url_for('auth.login'))



@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    print("in signup post")
    insert_data()
    return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    return 'Logout'

'''
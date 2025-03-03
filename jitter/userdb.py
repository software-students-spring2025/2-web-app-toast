'''
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

        hashed_password = generate_password_hash(password)  # Hash password

# <<<<<<< HEAD
#         reg_user = {
#             "name": name,
#             "email": email,
#             "password": hashed_password  # Store hashed password
#         }

#         db = get_db()
#         users = db.user

#         if users.find_one({"email": email}) is None:
# =======
#         users = db['user']
#         if users.find_one({"email":email}) == None:
# >>>>>>> 3e564f9eb60c1e0775d7946144205d9e9c8ca681
            # users.insert_one(reg_user)
        #     return True
        # else:
        #     return False

def check_user():
    if request.method == 'POST':
        print("in check_user")
        db = get_db()
        users = db['user']
        email = request.form['email']
        password = request.form['password']

# <<<<<<< HEAD
#         db = get_db()
#         users = db.user

#         user_data = users.find_one({"email": email})

#         if user_data is None:
#             return False, ""
#         else:
#             # Check hashed password
#             if check_password_hash(user_data["password"], password):
#                 return True, user_data["name"]
#             else:
#                 return False, ""
# =======
#         login_user = {
#             "email": email,
#             "password": password
#         }

#         print(email)
#         print(password)
#         user_data = users.find_one(login_user)
#         if user_data == None:
#             print("user not found")
#             return False, ""
#         else:
#             print("user found")
#             return True, user_data["name"]
# >>>>>>> 3e564f9eb60c1e0775d7946144205d9e9c8ca681
'''
from flask import Flask, render_template, request, redirect, abort, url_for, make_response, g
from dotenv import load_dotenv
from .auth import auth as auth_blueprint
from .dbconnect import get_db
from .review import review as review_blueprint  
def create_app():
    app = Flask(__name__)
    db = get_db()

    app.register_blueprint(auth_blueprint)

# <<<<<<< HEAD
#     # blueprint for non-auth parts of app
#     app.register_blueprint(main_blueprint)
# =======
#     app.register_blueprint(main_blueprint)    
# >>>>>>> 3e564f9eb60c1e0775d7946144205d9e9c8ca681
    app.register_blueprint(review_blueprint)
    return app

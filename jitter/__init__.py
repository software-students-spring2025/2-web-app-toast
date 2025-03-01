from flask import Flask, render_template, request, redirect, abort, url_for, make_response, g
from dotenv import load_dotenv
from .auth_routes import auth as auth_blueprint
from .main import main as main_blueprint
from .dbconnect import get_db

def create_app():
    app = Flask(__name__)
    db = get_db()

    app.register_blueprint(auth_blueprint)

    app.register_blueprint(main_blueprint)    

    return app

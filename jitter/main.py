from flask import Blueprint, render_template
#from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')
    #return 'index'

@main.route('/profile')
def profile():
    return render_template('profile.html')
    #return 'profile'
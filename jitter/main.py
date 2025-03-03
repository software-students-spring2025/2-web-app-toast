'''
from flask import Blueprint, render_template
# <<<<<<< HEAD
# from flask import request, jsonify
# from flask import Flask
# from flask_pymongo import PyMongo
# fmport os
# from dotenv import load_dotenv

# #from . import db
# =======
# >>>>>>> 3e564f9eb60c1e0775d7946144205d9e9c8ca681

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')
    #return 'index'

@main.route('/add_restaurant', methods=['POST'])
def add_restaurant():
    data = request.json  # Get JSON data from request

    if not data or 'name' not in data or 'rating' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    # Create the restaurant object
    new_restaurant = {
        "name": data["name"],
        "rating": data["rating"],
        "price": data.get("price", 0),  # Default to 0 if not provided
        "description": data.get("description", ""),
        "image_url": data.get("image_url", "https://via.placeholder.com/200")
    }

    # Insert into MongoDB
    restaurants_collection.insert_one(new_restaurant)
    
    return jsonify({"message": "Restaurant added successfully"}), 201


@main.route('/profile')
def profile():
    return render_template('profile.html')
    #return 'profile'
    '''
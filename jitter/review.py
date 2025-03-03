from flask import Blueprint, render_template, request, redirect, url_for
from .dbconnect import get_db 
from datetime import datetime 

review = Blueprint('review', __name__)
print('hi')
@review.route('/add-review', methods = ['GET'])
def add_review_form():
    return render_template('add_review.html')

@review.route('/add-review', methods = ['POST'])
def add_review():
    if(request.method == 'POST'):
        restaurant_name = request.form.get('restaurant_name')
        rating = int(request.form.get('rating'))
        review_text = request.form.get('review_text')
        if not restaurant_name:
            return "Please provide a restaurant name", 400
        if rating < 1 or rating > 5:
            return "Rating must be between 1 and 5", 400
        new_review = {"restaurant_name": restaurant_name, "rating": rating, "review_text": review_text, "created_at": datetime.now()}
        db = get_db()
        reviews = db['reviews']
        reviews.insert_one(new_review)
        return redirect(url_for('main.index'))
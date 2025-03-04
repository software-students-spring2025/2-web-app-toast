from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,  # Add this
    url_for,
)
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
import pymongo
from bson.objectid import ObjectId
#from .userdb import insert_data, check_user
import datetime
from flask import session

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


connection = pymongo.MongoClient(
    os.getenv("MONGO_URI")
)

db = connection["Jitter"]
restaurants_collection = db["restaurants"]
reviews_collection = db["reviews"]
users_collection = db["users"]


# ✅ Home Route - Render the homepage
@app.route("/")
def index():
    # Check if the user is already logged in

    # If the user is NOT logged in, fetch restaurant data and show login page
    restaurants = list(
        restaurants_collection.find({}, {"_id": 0})
    )  # Fetch restaurants from MongoDB
    user = session.get("user", None)   # Debugging print

    recent_reviews = list(reviews_collection.find().sort("created_at", -1).limit(5))
    if "user" in session:
        #return redirect(url_for("profile"))  # Redirect to profile if logged in
        return render_template(
            "base.html", restaurants=restaurants, user=user
        )



# ✅ API - Add a restaurant
@app.route("/add_restaurant", methods=["POST"])
def add_restaurant():
    data = (
        request.json
        if request.content_type == "application/json"
        else request.form.to_dict()
    )

    if not data or "name" not in data or "rating" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_restaurant = {
        "name": data["name"],
        "rating": float(data["rating"]),
        "price": data.get("price", 0),
        "description": data.get("description", ""),
        "image_url": data.get("image_url", "https://via.placeholder.com/200"),
    }

    restaurants_collection.insert_one(new_restaurant)
    return jsonify({"message": "Restaurant added successfully"}), 201


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip().lower()  # Normalize query

    if not query:
        return "No search term provided", 400

    # Find the restaurant in MongoDB (case-insensitive search)
    restaurant = restaurants_collection.find_one({"name": query})

    if not restaurant:
        return "Restaurant not found", 404

    # Get all reviews for this restaurant
    reviews = list(reviews_collection.find({"restaurant_name": query}).sort("created_at", -1))

    if "reviews" not in restaurant or not restaurant["reviews"]:
        restaurant["reviews"] = reviews

    return render_template("restaurant_details.html", restaurant=restaurant, reviews=reviews)




# ✅ Profile Page
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")

    username = session["user"]["name"]

    # Fetch reviews from the database
    db_reviews = list(reviews_collection.find({"user": username}).sort("created_at", -1))

    # Fetch new reviews stored in session
    session_reviews = session.get("new_reviews", [])

    # Combine session-stored reviews with database-stored reviews
    all_reviews = session_reviews + db_reviews

    return render_template("profile.html", user=session["user"], reviews=all_reviews)


@app.route("/base")
def base():
    return render_template("base.html")


@app.route("/add-review", methods=["GET"])
def add_review_form():
    # Simply render the add_review.html template when users visit the page
    return render_template("add_review.html")


@app.route("/add-review", methods=["POST"])
def add_review():
    if "user" not in session:
        return redirect("/login")  # Ensure user is logged in

    user = session["user"]["name"]  # Get logged-in username
    restaurant_name = request.form.get("restaurant_name", "").strip().lower()
    review_text = request.form.get("review_text")
    cuisine = request.form.get("cuisine", "").strip()

    # Validate rating
    try:
        rating = int(request.form.get("rating", 0))
        if rating < 1 or rating > 5:
            return "Rating must be between 1 and 5", 400
    except ValueError:
        return "Invalid rating format", 400

    if not restaurant_name or not review_text:
        return "Please provide both a restaurant name and your review", 400

    # Check if the restaurant already exists (case-insensitive search)
    existing_restaurant = restaurants_collection.find_one({"name": restaurant_name})

    # Create the review object
    new_review = {
        "user": user,
        "restaurant_name": restaurant_name,
        "rating": rating,
        "review_text": review_text,
        "cuisine": cuisine if cuisine else None,
        "created_at": datetime.datetime.now(),
    }

    # Insert review into the database and get its ObjectId
    inserted_review = reviews_collection.insert_one(new_review)
    new_review["_id"] = str(inserted_review.inserted_id)  # Convert ObjectId to string

    if existing_restaurant:
        # Append the new review to the existing restaurant
        restaurants_collection.update_one(
            {"name": restaurant_name},
            {
                "$push": {"reviews": new_review},
                "$set": {"cuisine": cuisine} if cuisine else {}
            }
        )
    else:
        # Create new restaurant entry with initial review
        new_restaurant = {
            "name": restaurant_name,
            "rating": float(rating),
            "cuisine": cuisine if cuisine else "Not specified",
            "reviews": [new_review],
            "created_at": datetime.datetime.now(),
        }
        restaurants_collection.insert_one(new_restaurant)

    # Store the new review in session
    if "new_reviews" not in session:
        session["new_reviews"] = []

    session["new_reviews"].append(new_review)  # Now safe to store

    return redirect(url_for("restaurant_details", restaurant_name=restaurant_name))


@app.route("/restaurant/<restaurant_name>")
def restaurant_details(restaurant_name):
    restaurant_name = restaurant_name.strip().lower()  # Normalize name
    restaurant = restaurants_collection.find_one({"name": restaurant_name})

    if not restaurant:
        return "Restaurant not found", 404

    # Fetch all reviews for this restaurant
    reviews = list(reviews_collection.find({"restaurant_name": restaurant_name}).sort("created_at", -1))

    return render_template("restaurant_details.html", restaurant=restaurant, reviews=reviews)

@app.route("/delete-review/<review_id>", methods=["POST"])
def delete_review(review_id):
    review = reviews_collection.find_one({"_id": ObjectId(review_id)})

    if not review:
        return "Review not found", 404

    # Normalize restaurant name before updating
    restaurant_name = review["restaurant_name"].strip().lower()

    # Delete the review from the `reviews` collection
    reviews_collection.delete_one({"_id": ObjectId(review_id)})

    # Remove the review from the associated restaurant's review list
    restaurants_collection.update_one(
        {"name": restaurant_name},
        {"$pull": {"reviews": {"_id": ObjectId(review_id)}}}
    )

    return redirect(url_for("restaurant_details", restaurant_name=restaurant_name))

@app.route("/edit-review/<review_id>")
def edit_review(review_id):
    """Render the edit review page."""
    review = reviews_collection.find_one({"_id": ObjectId(review_id)})

    if not review:
        return "Review not found", 404

    return render_template("edit_review.html", review=review)


@app.route("/update-review/<review_id>", methods=["POST"])
def update_review(review_id):
    """Update the review in the database."""
    new_rating = int(request.form.get("rating"))
    new_review_text = request.form.get("review_text")

    # Update the review in the `reviews` collection
    reviews_collection.update_one(
        {"_id": ObjectId(review_id)},
        {"$set": {"rating": new_rating, "review_text": new_review_text, "updated_at": datetime.datetime.now()}}
    )

    # Find the restaurant associated with this review
    review = reviews_collection.find_one({"_id": ObjectId(review_id)})
    restaurant_name = review["restaurant_name"]

    # Update the review inside the restaurant's reviews list
    restaurants_collection.update_one(
        {"name": restaurant_name, "reviews._id": ObjectId(review_id)},
        {"$set": {"reviews.$.rating": new_rating, "reviews.$.review_text": new_review_text}}
    )

    return redirect(url_for("restaurant_details", restaurant_name=restaurant_name))


    
@app.route("/recent-reviews")
def recent_reviews():
    # Fetch the most recent reviews from your database
    recent_reviews = list(
        reviews_collection.find().sort("created_at", -1).limit(10)
    )
    
    return render_template("recent_reviews.html", reviews=recent_reviews)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user exists in database
        user_data = users_collection.find_one({"email": email, "password": password})

        if user_data is None:
            return redirect('/login')  # Redirect back to login on failure
        
        # Store user information in session
        session['user'] = {
            "name": user_data["name"],  # Store the name of the user
            "email": user_data["email"]
        }

        return redirect('/profile')  # Redirect to the profile page


@app.route('/signup')
def signup():
    print("route signup get")
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    #print("in signup post")
    if request.method == 'POST':
        print("request method post")
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = {}
        new_user['name'] = name
        new_user['email'] = email
        new_user['password'] = password

        if users_collection.find_one({"email":email}) == None:
            users_collection.insert_one(new_user)
            print("signup successful")
        else:
            print("signup unsuccessful")
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect('/login')  # Redirect to login page


# ✅ Start Flask Application
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)

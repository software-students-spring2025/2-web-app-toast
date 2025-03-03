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
import datetime

app = Flask(__name__)

# Load environment variables
load_dotenv()

connection = pymongo.MongoClient(
    os.getenv("MONGO_URI")
)

db = connection["Jitter"]
restaurants_collection = db["restaurants"]
reviews_collection = db["reviews"]


# ✅ Home Route - Render the homepage
@app.route("/")
def index():
    restaurants = list(
        restaurants_collection.find({}, {"_id": 0})
    )  # Fetch restaurants from MongoDB
    recent_reviews = list(reviews_collection.find().sort("created_at", -1).limit(5))
    return render_template(
        "index.html", restaurants=restaurants, recent_reviews=recent_reviews
    )  # FIX: render_template now works!


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
    query = request.args.get("query")  # Get search term from the form

    if not query:
        return "No search term provided", 400

    # Find the restaurant in MongoDB (case-insensitive search)
    restaurant = restaurants_collection.find_one(
        {"name": {"$regex": query, "$options": "i"}}
    )

    if not restaurant:
        return "Restaurant not found", 404

    # Get all reviews for this restaurant
    reviews = list(reviews_collection.find({"restaurant_name": restaurant["name"]}).sort("created_at", -1))
    
    # If the restaurant doesn't have its own reviews array, include the ones we just fetched
    if "reviews" not in restaurant or not restaurant["reviews"]:
        restaurant["reviews"] = reviews


    return render_template("reviews.html", restaurant=restaurant, reviews=reviews)



# ✅ Profile Page
@app.route("/profile")
def profile():

    username = "ethan"

    print(f"🔍 Fetching reviews for: {username}")

    reviews = list(reviews_collection.find({"username": username}).sort("created_at", -1))

    if not reviews:
        return render_template("profile.html", user={"name": username, "age": "Unknown", "location": "Unknown"}, reviews=[])

    user = {
        "name": username,
        "age": "Unknown",
        "location": "Unknown"
    }

    print(f"✅ Rendering profile.html with {len(reviews)} reviews")

    return render_template("profile.html", user=user, reviews=reviews)




@app.route("/add-review", methods=["GET"])
def add_review_form():
    # Simply render the add_review.html template when users visit the page
    return render_template("add_review.html")

@app.route("/add-review", methods=["POST"])
def add_review():
    if request.method == "POST":
        # Extract form data
        user = request.form.get("user")  # User's name
        restaurant_name = request.form.get("restaurant_name")
        review_text = request.form.get("review_text")
        cuisine = request.form.get("cuisine", "").strip()

        # Validate rating and convert safely
        try:
            rating = int(request.form.get("rating", 0))
            if rating < 1 or rating > 5:
                return "Rating must be between 1 and 5", 400
        except ValueError:
            return "Invalid rating format", 400

        # Validation checks
        if not restaurant_name or not user:
            return "Please provide both a restaurant name and your name", 400

        # Create the review object
        new_review = {
            "user": user,
            "restaurant_name": restaurant_name,
            "rating": rating,
            "review_text": review_text,
            "cuisine": cuisine if cuisine else None,
            "created_at": datetime.datetime.now(),
        }

        # Insert review into the reviews collection
        reviews_collection.insert_one(new_review)

        # Check if the restaurant exists
        existing_restaurant = restaurants_collection.find_one({"name": restaurant_name})

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

        return redirect(url_for("index"))



@app.route("/restaurant/<restaurant_name>")
def restaurant_details(restaurant_name):
    # Find the restaurant by name
    restaurant = restaurants_collection.find_one({"name": restaurant_name})

    if not restaurant:
        return "Restaurant not found", 404

    # Fetch all reviews for this restaurant
    reviews = reviews_collection.find({"restaurant_name": restaurant_name}).sort(
        "created_at", -1
    )

    return render_template(
        "restaurant_details.html", restaurant=restaurant, reviews=reviews
    )

@app.route("/delete-review/<review_id>", methods=["POST"])
def delete_review(review_id):
    # Find the review to delete
    review = reviews_collection.find_one({"_id": ObjectId(review_id)})

    if not review:
        return "Review not found", 404

    # Delete the review from the `reviews` collection
    reviews_collection.delete_one({"_id": ObjectId(review_id)})

    # Remove the review from the associated restaurant's review list
    restaurants_collection.update_one(
        {"name": review["restaurant_name"]},
        {"$pull": {"reviews": {"_id": ObjectId(review_id)}}}
    )

    return redirect(url_for("restaurant_details", restaurant_name=review["restaurant_name"]))

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

# ✅ Start Flask Application
if __name__ == "__main__":
    app.run(debug=True)

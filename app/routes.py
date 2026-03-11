from flask import request, render_template, jsonify
from datetime import datetime
import requests
from app import myapp

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# home page
@myapp.route("/")
def home():
    sort = request.args.get("sort", "latest")
    page = int(request.args.get("page", 1))

    posts = [
        {
            "id": 101,
            "title": "Garlic Butter Shrimp Pasta",
            "author_username": "Amy",
            "minutes": 25,
            "difficulty": "Easy",
            "description": "Creamy, garlicky shrimp pasta with lemon and parsley.",
            "tags": ["pasta", "seafood", "quick"],
            "saved": False,
            "like_count": 12,
        }
    ]

    recommended = [
        {"id": 901, "title": "Avocado Toast 3 Ways", "minutes": 10, "category": "Breakfast"},
        {"id": 902, "title": "Spicy Ramen Upgrade", "minutes": 15, "category": "Quick"},
    ]

    return render_template(
        "home.html",
        feed_title="Latest Recipes",
        sort=sort,
        page=page,
        has_next=True,
        posts=posts,
        recommended=recommended,
        current_user=None,   # or your user object
        current_year=datetime.now().year
    )

# Search recipes
@myapp.route("/api/search")
def search():
    query = request.args.get("q") #It comes from the URL. For example, if the user searches for "chicken", the URL would be "/api/search?q=chicken". The "q" parameter is used to pass the search query.

    response = requests.get(
        f"{BASE_URL}/search.php",
        params={"s": query} #The "s" parameter is used to specify the search query for meals. The API will return meals that match the search query provided in the "q" parameter of the URL. ex search.php?s=meal_name
    )

    data = response.json()

    # If no results
    if data["meals"] is None:
        return jsonify({"results": []})

    # Clean the response
    results = [
        {
            "id": meal["idMeal"],
            "title": meal["strMeal"],
            "image": meal["strMealThumb"]
        }
        for meal in data["meals"]
    ]

    return jsonify({"results": results})

@myapp.route("/api/explore")
def explore():
    return "<h1>Explore Results</h1>"

@myapp.route("/my_recipes")
def my_recipes():
    return "<h1>My Recipes</h1>"

@myapp.route("/post_recipe")
def post_recipe():
    return "<h1>Post Recipe</h1>"

@myapp.route("/recipe_detail")
def recipe_detail():
    return "<h1>Recipe Detail</h1>"

@myapp.route("/login")
def login():
    return "<h1>Login</h1>"

@myapp.route("/signup")
def signup():
    return "<h1>Sign Up</h1>"

@myapp.route("/profile")
def profile():
    return "<h1>Profile</h1>"

@myapp.route("/save_recipe")
def save_recipe():
    return "<h1>Save Recipe</h1>"

@myapp.route("/saved")
def saved():
    return "<h1>Saved Recipes</h1>"
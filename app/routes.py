from flask import request, jsonify
import requests
from app import myapp

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# home page
@myapp.route("/")
def home():
    return "Welcome to the Recipe API! Use /api/search?q=meal_name to search for recipes."

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
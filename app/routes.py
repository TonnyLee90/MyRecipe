from flask import abort, flash, request, render_template, jsonify, url_for, render_template, redirect, current_app
from app.models import User, Recipe
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import requests
from app import myapp, db
from app.form import LoginForm, SaveRecipeForm, UnsaveRecipeForm, SignupForm, PostRecipeForm, DeleteForm, UnsaveRecipeForm

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# home page
@myapp.route("/")
def home():
    recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    saved_ids = set()
    if current_user.is_authenticated:
        saved_ids = {r.id for r in current_user.saved.all()}
    recommended = []

    for _ in range(2):
        res = requests.get("https://www.themealdb.com/api/json/v1/1/random.php")
        if res.status_code == 200:
            data = res.json()
            meal = data["meals"][0]

            recommended.append({
                "id": meal["idMeal"],  # API id
                "title": meal["strMeal"],
                "category": meal["strCategory"]
            })
    
    return render_template(
        "home.html", recipes =recipes, saved_ids=saved_ids,
        recommended=recommended,
        current_user=current_user,
        current_year=datetime.now().year
    )

API_SEARCH = "https://www.themealdb.com/api/json/v1/1/search.php"
@myapp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    scope = request.args.get("scope", "local")

    meals = []
    error = None

    if not q:
        return render_template("search.html", q="", meals=[], error=None)

    # api search
    if scope == "api":
        try:
            resp = requests.get(API_SEARCH, params={"s": q}, timeout=6)
            resp.raise_for_status()
            data = resp.json()

            raw = data.get("meals") or []
            for item in raw:
                instructions = item.get("strInstructions") or ""
                meals.append({
                    "id": item.get("idMeal"),
                    "name": item.get("strMeal"),
                    "category": item.get("strCategory"),
                    "area": item.get("strArea"),
                    "instructions": instructions,
                    "thumb": item.get("strMealThumb"),
                    "tags": (item.get("strTags") or "").split(",") if item.get("strTags") else [],
                    "instructions_preview": instructions[:220],
                    "source": "api",
                })
        except Exception as e:
            current_app.logger.exception("TheMealDB search failed: %s", e)
            error = "Could not fetch results from TheMealDB right now."

        return render_template("search.html", q=q, meals=meals, error=error)

    # local db search (default)
    try:
        meals = (Recipe.query.filter(Recipe.title.ilike(f"%{q}%"),).order_by(Recipe.id.desc()).limit(50).all())
    except Exception as e:
        current_app.logger.exception("Local DB search failed: %s", e)
        error = "Could not search local recipes right now."

    return render_template("search.html", q=q, meals=meals, error=error)

@myapp.route("/post_recipe", methods=["GET", "POST"])
@login_required
def post_recipe():
    form = PostRecipeForm()

    if form.validate_on_submit():
        recipe = Recipe(title=form.name.data, body=form.body.data,
                        ingredients=form.ingredients.data,
                        instructions=form.instructions.data,
                        author=current_user)
        # Save the data entered in the form to the db
        db.session.add(recipe)
        db.session.commit()

        flash('Recipe posted!')
        return redirect(url_for("recipe_detail", recipe_id=recipe.id))

    return render_template("post_recipe.html", form=form)

@myapp.route('/recipe/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe is None:
        return render_template("404.html"), 404 
    if recipe.author != current_user: # Check if the recipe's user != current_user
        flash('You do not have permission to delete')
        return redirect(url_for('home'))
    # delete the post
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted!')
    return redirect(request.referrer)

# Route for local recipe details
@myapp.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    if recipe is None:
        return render_template("404.html"), 404 

    return render_template("recipe_detail.html", recipe=recipe, back_url=url_for("my_recipes"))

def _extract_ingredients(meal: dict):
    items = []
    for i in range(1, 21):
        ing = (meal.get(f"strIngredient{i}") or "").strip()
        meas = (meal.get(f"strMeasure{i}") or "").strip()
        if ing:
            items.append(f"{meas} {ing}".strip())
    return items

# API recipe details route (for explore/search results)
@myapp.route("/external/<meal_id>")
def external_recipe(meal_id):
    API_LOOKUP = "https://www.themealdb.com/api/json/v1/1/lookup.php"

    res = requests.get(API_LOOKUP, params={"i": meal_id})
    data = res.json()
    meal = data["meals"][0]
    ingredients = _extract_ingredients(meal)

    return render_template(
        "external_recipe_detail.html",
        title=meal["strMeal"],
        category=meal["strCategory"],
        instructions=meal["strInstructions"],
        image=meal["strMealThumb"],
        ingredients=ingredients
    )

@myapp.route("/my_recipes")
@login_required
def my_recipes():
    form = DeleteForm()
    recipes = (Recipe.query.filter_by(author_id=current_user.id).order_by(Recipe.created_at.desc()).all())
    return render_template("my_recipes.html", recipes=recipes, form=form)

# Account
@myapp.route('/login', methods=['GET', 'POST'])
def login():
    # redirect the logged user to home page when they go to login page again
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # to check if the username entered in the form == the username in the db
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data): # check if the user exist in the db and if the entered password is matched with the hash_password in the db
            login_user(user)
            flash("Logged in!", "success")                                                             
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful! Please check your username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@myapp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists", "error")
            return redirect(url_for("signup"))

        user = User(username=form.username.data)
        user.set_password(form.password.data)

        # add the user to the db
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=form)

# logout
@myapp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("home"))

@myapp.route("/save/<int:recipe_id>", methods=["POST"])
@login_required
def save_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        abort(404)

    # already saved?
    if current_user.saved.filter(Recipe.id == recipe_id).first() is None:
        current_user.saved.append(recipe)
        db.session.commit()

    return redirect(request.referrer)


@myapp.route("/unsave/<int:recipe_id>", methods=["POST"])
@login_required
def unsave_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        abort(404)
    if current_user.saved.filter(Recipe.id == recipe_id).first() is not None:
        current_user.saved.remove(recipe)
        db.session.commit()

    return redirect(request.referrer or url_for("home"))

@myapp.route("/favorites")
@login_required
def favorites():
    saved_recipes = current_user.saved.all()  # because lazy="dynamic"
    return render_template("favorites.html", saved_recipes=saved_recipes)

@myapp.route("/explore")
def explore():
    """
    Fetch 8 random meals from TheMealDB and render the explore page.
    Uses the public random endpoint: https://www.themealdb.com/api/json/v1/1/random.php
    """
    API_RANDOM = "https://www.themealdb.com/api/json/v1/1/random.php"

    meals = []
    seen_ids = set()
    max_attempts = 16

    for _ in range(max_attempts):
        if len(meals) >= 8:
            break
        try:
            resp = requests.get(API_RANDOM, timeout=6)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            current_app.logger.warning("TheMealDB fetch failed: %s", e)
            break

        item = None
        if data and data.get("meals"):
            item = data["meals"][0]

        if not item:
            continue

        meal_id = item.get("idMeal")
        if meal_id in seen_ids:
            continue

        meal = {
            "id": meal_id,
            "name": item.get("strMeal"),
            "category": item.get("strCategory"),
            "area": item.get("strArea"),
            "instructions": item.get("strInstructions") or "",
            "thumb": item.get("strMealThumb"),          
            "tags": (item.get("strTags") or "").split(",") if item.get("strTags") else [],
            "instructions_preview": (item.get("strInstructions") or "")[:220],
            "created_at": datetime.utcnow(),
        }

        meals.append(meal)
        seen_ids.add(meal_id)

    return render_template("explore.html", meals=meals)

@myapp.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
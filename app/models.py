from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login_manager

# To reload a user from the session.
# so Flask-Login knows who is logged in 
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# association table: users saving recipes
saved_recipes = db.Table(
    "saved_recipes",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipes.id"), primary_key=True),
)

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # recipes the user posts
    recipes = db.relationship("Recipe", back_populates="author", cascade="all, delete-orphan") # all-delete-orphan cascade ensures child entities are automatically deleted if the parent is deleted 

    # recipes the user saves
    saved = db.relationship(
        "Recipe",
        secondary=saved_recipes,
        back_populates="saved_by",
        lazy="dynamic",
    )

    def set_password(self, password: str) -> None:
        # encrypt the password and store the hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", back_populates="recipes")

    saved_by = db.relationship(
        "User",
        secondary=saved_recipes,
        back_populates="saved",
        lazy="dynamic",
    )
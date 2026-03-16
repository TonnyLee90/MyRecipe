from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv

load_dotenv()
myapp = Flask(__name__)
myapp.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
myapp.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
myapp.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # disable Flask-SQLAlchemy event system to save resources

db = SQLAlchemy()
db.init_app(myapp)

migrate = Migrate()
migrate.init_app(myapp, db)

login_manager = LoginManager()
login_manager.init_app(myapp)
# Custom message to notify the user
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"
# Redirect URL for unauthorized access
login_manager.login_view = 'login'

from app import routes # prevents circular import

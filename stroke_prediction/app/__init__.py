import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from mongoengine import connect

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
login_manager = LoginManager()  # Initialize LoginManager

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configurations
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLITE_DATABASE_URI')
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)

    # Set login view (Redirect user to login page if they are not authenticated)
    login_manager.login_view = "auth.login"

    # Import and register blueprints
    from app.views.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from app.views.profile import profile
    app.register_blueprint(profile, url_prefix='/profile')

    # Connect to MongoDB
    connect(host=app.config["MONGO_URI"])

    # Define the user_loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Assuming you have a `User` model for SQLAlchemy
        from app.models.user import User  # Make sure to import your User model
        return User.query.get(int(user_id))

    # Route
    @app.route('/')
    def home():
        return render_template('home.html')

    return app

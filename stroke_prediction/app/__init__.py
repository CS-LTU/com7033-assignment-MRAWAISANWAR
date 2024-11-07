import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from mongoengine import connect
# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configurations
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLITE_DATABASE_URI')
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Import and register blueprints here to avoid circular imports
    from app.views.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

     # Connect to MongoDB
    connect(host=app.config["MONGO_URI"])

    # Sample route
    @app.route('/')
    def home():
        return render_template('home.html')

    return app
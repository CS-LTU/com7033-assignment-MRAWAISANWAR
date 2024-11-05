from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app import db, bcrypt
from app.models.user import User
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        access_level = data.get('access_level')

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "User already exists"}), 400

        # Create new user and hash the password
        new_user = User(
            username=username,
            email=email,
            access_level=access_level
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        # Verify user and password
        if user and user.check_password(password):
            access_token = create_access_token(identity={"id": user.id, "access_level": user.access_level})
            return jsonify({"access_token": access_token}), 200

        return jsonify({"message": "Invalid credentials"}), 401

    return render_template('auth/login.html')
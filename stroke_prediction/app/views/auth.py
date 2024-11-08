from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt
from app.models.user import User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash("User already exists", "danger")
            return redirect(url_for('auth.register'))

        # Create new user and hash the password
        new_user = User(
            username=username,
            email=email,
            role=role
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('User successfully registered!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # Verify user and password
        if user and user.check_password(password):
            login_user(user)  # Log the user in
            flash('Login successful', 'success')
            return redirect(url_for('home'))

        flash('Invalid credentials', 'danger')

    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    logout_user()  # Logs the user out and ends the session
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

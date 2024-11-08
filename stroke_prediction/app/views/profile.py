# app/views/profile.py

from flask import Blueprint, render_template

# Define the profile blueprint
profile = Blueprint('profile', __name__)

# Define the settings route
@profile.route('/settings', methods=['GET'])
def settings():
    return render_template('profile/settings.html')

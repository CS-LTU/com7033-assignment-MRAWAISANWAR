# views/profile.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db

profile = Blueprint('profile', __name__)

@profile.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template('profile/settings.html')

@profile.route('/update_name', methods=['POST'])
@login_required
def update_name():
    new_name = request.form.get('new_name')
    if not new_name:
        flash('Name cannot be empty', 'danger')
        return redirect(url_for('profile.settings'))
    
    current_user.name = new_name
    db.session.commit()
    flash('Name updated successfully', 'success')
    return redirect(url_for('profile.settings'))

@profile.route('/update_password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    
    if not current_password or not new_password:
        flash('Both current and new passwords are required', 'danger')
        return redirect(url_for('profile.settings'))
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('profile.settings'))
    
    current_user.set_password(new_password)
    db.session.commit()
    flash('Password updated successfully', 'success')
    return redirect(url_for('profile.settings'))
# stroke_prediction/app/views/patient.py

from flask import Blueprint, render_template, redirect, url_for, flash
from app.forms.patient_form import PatientForm
from app.models.patient import Patient  # Import the Patient model from your MongoDB schema
from datetime import datetime
from flask_login import current_user  # Assuming you’re using Flask-Login

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/add', methods=['GET', 'POST'])
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        # Create and save a new patient record
        new_patient = Patient(
            patient_id=form.patient_id.data,
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            ever_married=form.ever_married.data,
            work_type=form.work_type.data,
            residence_type=form.residence_type.data,
            heart_disease=form.heart_disease.data,
            hypertension=form.hypertension.data,
            avg_glucose_level=form.avg_glucose_level.data,
            bmi=form.bmi.data,
            smoking_status=form.smoking_status.data,
            stroke_risk=form.stroke_risk.data,
            record_entry_date=datetime.now(),
            created_by=current_user.username if current_user.is_authenticated else "unknown"
        )
        new_patient.save()
        flash('Patient added successfully!', 'success')
        return redirect(url_for('patient.add_patient'))

    return render_template('patient/add_patient.html', form=form)

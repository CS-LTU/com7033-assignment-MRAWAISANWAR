# app/views/patient.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.forms.patient_form import PatientForm
from app.models.patient import Patient
from app.utils.prediction import StrokePredictor
from datetime import datetime
from flask_login import current_user, login_required
import traceback

patient_bp = Blueprint('patient', __name__)
stroke_predictor = StrokePredictor()

def map_binary_to_yes_no(value):
    """Convert '0'/'1' to 'No'/'Yes'"""
    return 'Yes' if value == '1' else 'No'

def map_smoking_status(status):
    """Map form smoking status to MongoDB expected format"""
    mapping = {
        'formerly smoked': 'Formerly Smoked',
        'never smoked': 'Never Smoked',
        'smokes': 'Smokes',
        'Unknown': 'Unknown'
    }
    return mapping.get(status, status)

def map_work_type(work):
    """Map form work type to MongoDB expected format"""
    mapping = {
        'Private': 'Private',
        'Self-employed': 'Self-Employed',
        'Govt_job': 'Govt Job',
        'children': 'Children',
        'Never_worked': 'Never Worked'
    }
    return mapping.get(work, work)

@patient_bp.route('/add', methods=['GET'])
@login_required
def add_patient():
    form = PatientForm()
    return render_template('patient/add_patient.html', form=form)

@patient_bp.route('/predict', methods=['POST'])
@login_required
def predict_risk():
    try:
        print("Received form data:", request.form)  # Debug print
        
        # Prepare patient data for prediction
        prediction_data = {
            'age': int(request.form['age']),
            'gender': request.form['gender'],
            'hypertension': request.form['hypertension'],
            'heart_disease': request.form['heart_disease'],
            'ever_married': request.form['ever_married'],
            'work_type': request.form['work_type'],
            'residence_type': request.form['residence_type'],
            'avg_glucose_level': float(request.form['avg_glucose_level']),
            'bmi': float(request.form['bmi']),
            'smoking_status': request.form['smoking_status']
        }
        
        # Get prediction
        risk_percentage = stroke_predictor.predict_risk(prediction_data)
        
        print("Predicted risk:", risk_percentage)  # Debug print
        
        # Prepare data for MongoDB (with correct mappings)
        new_patient = Patient(
            patient_id=request.form['patient_id'],
            name=request.form['name'],
            age=int(request.form['age']),
            gender=request.form['gender'],
            ever_married=request.form['ever_married'],
            work_type=map_work_type(request.form['work_type']),
            residence_type=request.form['residence_type'],
            heart_disease=map_binary_to_yes_no(request.form['heart_disease']),
            hypertension=map_binary_to_yes_no(request.form['hypertension']),
            avg_glucose_level=float(request.form['avg_glucose_level']),
            bmi=float(request.form['bmi']),
            smoking_status=map_smoking_status(request.form['smoking_status']),
            stroke_risk=risk_percentage,
            record_entry_date=datetime.now(),
            created_by=current_user.name
        )
        
        new_patient.save()
        
        return jsonify({
            'success': True,
            'risk': risk_percentage,
            'message': 'Patient data saved successfully'
        })
        
    except ValueError as e:
        print("Validation error:", str(e))  # Debug print
        print(traceback.format_exc())  # Print full traceback
        return jsonify({
            'success': False,
            'message': f'Invalid input data: {str(e)}'
        }), 400
        
    except Exception as e:
        print("Unexpected error:", str(e))  # Debug print
        print(traceback.format_exc())  # Print full traceback
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

@patient_bp.route('/search', methods=['GET'])
@login_required
def search_patient():
    patient_id = request.args.get('patient_id')
    
    if patient_id:
        patient = Patient.objects(patient_id=patient_id).first()
        
        if patient:
            return render_template('patient_details.html', patient=patient)
        else:
            flash('Patient not found', 'warning')
            return redirect(url_for('home'))
            
    return redirect(url_for('home'))
#views/process_patient.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app.forms.patient_form import PatientForm
from app.models.patient import Patient
from app.utils.prediction import StrokePredictor
from app.utils.id_generator import IDGenerator
from datetime import datetime
from flask_login import current_user, login_required
import traceback
import numpy as np
import json

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

def get_risk_level(risk_percentage):
    """Get risk level based on percentage"""
    if risk_percentage < 20:
        return "Low"
    elif risk_percentage < 40:
        return "Moderate"
    elif risk_percentage < 60:
        return "High"
    elif risk_percentage < 80:
        return "Very High"
    else:
        return "Critical"

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                          np.int16, np.int32, np.int64, np.uint8,
                          np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

@patient_bp.route('/add', methods=['GET'])
@login_required
def add_patient():
    form = PatientForm()
    return render_template('patient/add_patient.html', form=form)

@patient_bp.route('/predict', methods=['POST'])
@login_required
def predict_risk():
    try:
        # Prepare patient data for prediction
        prediction_data = {
            'age': request.form['age'],
            'gender': request.form['gender'],
            'hypertension': request.form['hypertension'],
            'heart_disease': request.form['heart_disease'],
            'ever_married': request.form['ever_married'],
            'work_type': request.form['work_type'],
            'residence_type': request.form['residence_type'],
            'avg_glucose_level': request.form['avg_glucose_level'],
            'bmi': request.form['bmi'],
            'smoking_status': request.form['smoking_status']
        }
        
        # Get prediction
        try:
            risk_percentage = float(stroke_predictor.predict_risk(prediction_data))
            risk_level = get_risk_level(risk_percentage)
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        
        # Prepare data for MongoDB
        try:
            new_patient = Patient(
                patient_id=IDGenerator.generate_patient_id(),
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
            
            # Use the custom JSON encoder for the response
            response = {
                'success': True,
                'patient_id': new_patient.patient_id,
                'name': new_patient.name,
                'risk': risk_percentage,
                'risk_level': risk_level,
                'message': 'Patient data saved successfully'
            }
            
            return json.dumps(response, cls=NumpyEncoder), 200, {'Content-Type': 'application/json'}
            
        except Exception as e:
            print(f"Error saving patient: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'message': f'Error saving patient data: {str(e)}'
            }), 500
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

@patient_bp.route('/search', methods=['GET'])
@login_required
def search_patient():
    patient_id = request.args.get('patient_id')

    print(f"Searching for patient: {patient_id}")  # Debug print

    
    if patient_id:
        patient = Patient.objects(patient_id=patient_id).first()
        
        if patient:
            return render_template('patient_details.html', patient=patient)
        else:
            flash('Patient not found', 'warning')
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
            # return redirect(url_for('home'))
            
    return redirect(url_for('home'))
# forms/patient_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class PatientForm(FlaskForm):
    patient_id = StringField('Patient ID', 
        validators=[DataRequired(), Length(min=6, max=6)])
    
    name = StringField('Name', 
        validators=[DataRequired()])
    
    age = IntegerField('Age', 
        validators=[DataRequired(), NumberRange(min=0, max=120)])
    
    gender = SelectField('Gender', 
        choices=[('Male', 'Male'), ('Female', 'Female')], 
        validators=[DataRequired()])
    
    ever_married = SelectField('Married', 
        choices=[('Yes', 'Yes'), ('No', 'No')], 
        validators=[DataRequired()])
    
    work_type = SelectField('Work Type', 
        choices=[
            ('Children', 'Children'),
            ('Govt Job', 'Government Job'),
            ('Never Worked', 'Never Worked'),
            ('Private', 'Private Sector'),
            ('Self-Employed', 'Self-Employed')
        ], 
        validators=[DataRequired()])
    
    residence_type = SelectField('Residence Type', 
        choices=[('Urban', 'Urban'), ('Rural', 'Rural')], 
        validators=[DataRequired()])
    
    heart_disease = SelectField('Heart Disease', 
        choices=[('Yes', 'Yes'), ('No', 'No')], 
        validators=[DataRequired()])
    
    heart_disease = SelectField('Heart Disease', 
        choices=[('Yes', 'Yes'), ('No', 'No')], 
        validators=[DataRequired()])
    
    hypertension = SelectField('Hypertension', 
        choices=[('Yes', 'Yes'), ('No', 'No')], 
        validators=[DataRequired()])
    
    avg_glucose_level = FloatField('Avg. Glucose Level', 
        validators=[DataRequired()])
    
    bmi = FloatField('BMI', 
        validators=[DataRequired()])
    
    smoking_status = SelectField('Smoking Status',
        choices=[
            ('Smokes', 'Currently Smoking'),
            ('Formerly Smoked', 'Former Smoker'),
            ('Never Smoked', 'Never Smoked'),
            ('Unknown', 'Unknown')
        ],
        validators=[DataRequired()])
    
    stroke_risk = IntegerField('Stroke Risk (%)', 
        validators=[DataRequired(), NumberRange(min=0, max=100)])
    
    submit = SubmitField('Add Patient')
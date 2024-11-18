# app/forms/patient_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, NumberRange, Length

class PatientForm(FlaskForm):
    
    name = StringField('Patient Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    
    age = IntegerField('Age', validators=[
        DataRequired(),
        NumberRange(min=5, max=120)
    ])
    
    gender = SelectField('Gender', choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    
    ever_married = SelectField('Ever Married', choices=[
        ('Yes', 'Yes'),
        ('No', 'No')
    ], validators=[DataRequired()])
    
    work_type = SelectField('Work Type', choices=[
        ('Private', 'Private Sector'),
        ('Self-employed', 'Self Employed'),
        ('Govt_job', 'Government Job'),
        ('children', 'Children'),
        ('Never_worked', 'Never Worked')
    ], validators=[DataRequired()])
    
    residence_type = SelectField('Residence Type', choices=[
        ('Urban', 'Urban'),
        ('Rural', 'Rural')
    ], validators=[DataRequired()])
    
    heart_disease = SelectField('Heart Disease', choices=[
        ('1', 'Yes'),
        ('0', 'No')
    ], validators=[DataRequired()])
    
    hypertension = SelectField('Hypertension', choices=[
        ('1', 'Yes'),
        ('0', 'No')
    ], validators=[DataRequired()])
    
    avg_glucose_level = FloatField('Avg. Glucose Level', validators=[
        DataRequired(),
        NumberRange(min=0)
    ])
    
    bmi = FloatField('BMI', validators=[
        DataRequired(),
        NumberRange(min=0, max=100)
    ])
    
    smoking_status = SelectField('Smoking Status', choices=[
        ('formerly smoked', 'Formerly Smoked'),
        ('never smoked', 'Never Smoked'),
        ('smokes', 'Currently Smoking'),
        ('Unknown', 'Unknown')
    ], validators=[DataRequired()])
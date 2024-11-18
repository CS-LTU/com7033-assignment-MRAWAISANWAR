from datetime import datetime
import random
from app.models.patient import Patient

class IDGenerator:
    @staticmethod
    def generate_patient_id():
        """
        Generates a valid 8-digit patient ID based on the current date and time,
        combined with a random sequence. Retries up to 5 times if validation fails.
        """

        max_attempts = 5
        
        for attempt in range(max_attempts):
            # Get current date components
            now = datetime.now()
            year_digit = str(now.year)[-1]  # Last digit of the year
            month_digits = str(now.month).zfill(2)  # Ensure 2 digits
            day_digits = str(now.day).zfill(2)  # Ensure 2 digits
            
            # Create date portion of the ID
            date_portion = f"{year_digit}{month_digits}{day_digits}"
            
            # Generate a random 4-digit sequence
            random_sequence = str(random.randint(0, 9999)).zfill(4)
            
            # Combine to create 8-digit ID
            patient_id = f"{date_portion}{random_sequence}"
            
            # Validate the generated ID
            if IDGenerator.validate_patient_id(patient_id):
                return str(patient_id)  # Return if valid
            else:
                print(f"Attempt {attempt + 1}: Generated invalid ID {patient_id}. Retrying...")
        
        # If all attempts fail, raise an exception or handle the failure
        raise ValueError("Failed to generate a valid patient ID after maximum attempts.")


    def check_patient_id(patient_id):

        # Try to fetch the patient with the given patient_id
        patient = Patient.objects(patient_id=patient_id).first()
        
        # Check if a matching document was found
        if not patient:
            return True
        else:
            return False
        

    @staticmethod
    def validate_patient_id(patient_id):
        """
        Validates the format and structure of a patient ID.
        Ensures it is 8 digits and has a valid date component.
        """
        if not patient_id or not isinstance(patient_id, str):
            return False
        
        if len(patient_id) != 9 or not patient_id.isdigit():
            return False
        
        if IDGenerator.check_patient_id(str(patient_id)):
            return True

        return False
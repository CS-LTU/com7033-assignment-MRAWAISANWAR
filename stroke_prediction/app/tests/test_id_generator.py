import pytest
from app.utils.id_generator import IDGenerator

def test_generate_patient_id_format(current_date_portion):
    """Test if generated ID has correct format"""
    patient_id = IDGenerator.generate_patient_id()
    
    assert isinstance(patient_id, str), "ID should be a string"
    assert len(patient_id) == 9, "ID should be 9 characters long"
    assert patient_id.isdigit(), "ID should only contain digits"
    assert patient_id[:5] == current_date_portion, "ID should start with current date"

def test_validate_patient_id(sample_valid_id, sample_invalid_ids):
    """Test ID validation function"""
    # Test valid ID
    assert IDGenerator.validate_patient_id(sample_valid_id), "Should validate correct ID format"
    
    # Test invalid IDs
    for invalid_id in sample_invalid_ids:
        assert not IDGenerator.validate_patient_id(invalid_id), f"Should reject invalid ID: {invalid_id}"

def test_check_patient_id():
    """Test if patient ID exists in database"""
    # Test with a new ID that shouldn't exist
    test_id = "123456789"
    assert IDGenerator.check_patient_id(test_id), "Should return True for non-existent ID"

def test_id_uniqueness():
    """Test if generated IDs are unique"""
    ids = set()
    for _ in range(5):  # Generate 5 IDs
        new_id = IDGenerator.generate_patient_id()
        assert new_id not in ids, "Generated IDs should be unique"
        ids.add(new_id)
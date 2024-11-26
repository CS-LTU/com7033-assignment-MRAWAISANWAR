import pytest
from app.utils.prediction import StrokePredictor

def test_high_risk_prediction(high_risk_patient):
    predictor = StrokePredictor()
    risk = predictor.predict_risk(high_risk_patient)
    assert risk > 30.0, "High risk patient should have risk > 30%"

def test_low_risk_prediction(low_risk_patient):
    predictor = StrokePredictor()
    risk = predictor.predict_risk(low_risk_patient)
    assert risk < 5.0, "Low risk patient should have risk < 5%"

def test_invalid_input(invalid_patient):
    predictor = StrokePredictor()
    with pytest.raises(ValueError) as exc_info:
        predictor.predict_risk(invalid_patient)
    assert "Age must be between 0 and 120" in str(exc_info.value)
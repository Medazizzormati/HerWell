from app.ai.safety import safety_precheck, safety_postcheck

def test_crisis_phrase_routes():
    assert safety_precheck("I want to die") is True

def test_normal_stress_does_not_route():
    assert safety_precheck("I am stressed about exams") is False

def test_diagnostic_claim_is_replaced():
    assert "diagnostic" in safety_postcheck("You definitely have depression").lower()

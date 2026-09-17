def calculate_priority(severity: str, confidence: float) -> str:
    """Apply the documented priority rules in order of precedence."""
    if severity == "High" or confidence >= 90:
        return "High"
    if severity == "Medium" or confidence >= 80:
        return "Medium"
    return "Low"


def calculate_severity(symptoms: str, confidence: float) -> str:
    """Estimate triage severity without adding a database field."""
    high_signals = ("collapse", "unable to stand", "seizure", "severe bleeding", "blood")
    medium_signals = ("fever", "swelling", "diarrhea", "vomit", "not eating", "weak")
    normalized = symptoms.lower()
    if any(signal in normalized for signal in high_signals):
        return "High"
    if any(signal in normalized for signal in medium_signals) or confidence >= 80:
        return "Medium"
    return "Low"
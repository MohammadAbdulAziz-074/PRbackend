DISEASE_RECOMMENDATIONS = {
    "Mastitis": [
        "Isolate affected animal",
        "Clean udder before milking",
        "Veterinary consultation within 24 hrs",
    ],
    "Milk Fever": [
        "Provide calcium supplementation",
        "Keep animal warm",
        "Immediate veterinary attention",
    ],
    "Foot Rot": [
        "Clean hoof",
        "Keep dry flooring",
        "Antibacterial treatment",
    ],
}


def generate_recommendations(disease: str, severity: str, symptoms: str) -> list[str]:
    """Return disease-specific immediate triage guidance."""
    if disease in DISEASE_RECOMMENDATIONS:
        return DISEASE_RECOMMENDATIONS[disease]
    if severity == "High":
        return ["Keep the animal warm", "Contact veterinarian immediately"]
    if severity == "Medium":
        return ["Monitor temperature and hydration", "Contact a veterinarian soon"]
    return ["Provide clean water and observe symptoms"]
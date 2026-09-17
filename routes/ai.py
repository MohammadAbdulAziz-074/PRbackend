from datetime import date

from flask import Blueprint, jsonify, request

from ai.gemini_predictor import AIConfigurationError, AIProviderError, predict_disease
from ai.priority_engine import calculate_priority
from ai.recommendation_engine import generate_recommendations
from database import db
from models import Animal, Complaint
from routes.complaints import _generate_complaint_id


ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/analyze", methods=["POST"])
def analyze_symptoms():
    data = request.get_json(silent=True) if request.is_json else request.form
    data = data or {}
    animal_id = (data.get("animal_id") or "").strip()
    symptoms = (data.get("symptoms") or "").strip()
    temperature = data.get("temperature")
    milk_reduction = data.get("milk_reduction")
    image = request.files.get("image")

    if not animal_id or not symptoms:
        return jsonify({"error": "animal_id and symptoms are required"}), 400

    animal = Animal.query.get(animal_id)
    if not animal:
        return jsonify({"error": "Animal not found"}), 404

    try:
        prediction = predict_disease(
            symptoms,
            animal,
            temperature=temperature,
            milk_reduction=milk_reduction,
            image=image,
        )
    except AIConfigurationError as error:
        return jsonify({"error": str(error)}), 500
    except AIProviderError as error:
        return jsonify({"error": str(error)}), 500

    disease = str(prediction["disease"])
    confidence = round(float(prediction.get("confidence", 0)), 2)
    severity = prediction.get("severity", "Low")
    priority = calculate_priority(severity, confidence)
    recommendations = prediction.get("recommendations") or generate_recommendations(
        disease, severity, symptoms
    )

    complaint = Complaint(
        complaint_id=_generate_complaint_id(),
        animal_id=animal_id,
        complaint_date=date.today(),
        symptoms=symptoms,
        ai_prediction=disease,
        confidence=confidence,
        priority=priority,
        status="Submitted",
    )
    try:
        db.session.add(complaint)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "complaint_id": complaint.complaint_id,
        "animal_id": animal_id,
        "ai_prediction": disease,
        "confidence": confidence,
        "severity": severity,
        "priority": priority,
        "status": complaint.status,
        "recommendations": recommendations,
    }), 201
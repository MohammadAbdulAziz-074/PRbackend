from datetime import date, datetime

from flask import Blueprint, jsonify, request
from database import db
from models import Animal, Complaint

complaints_bp = Blueprint("complaints", __name__)

VALID_STATUSES = {
    "Submitted",
    "Vet Assigned",
    "Sample Collected",
    "Lab Testing",
    "Recovered",
}

VALID_PRIORITIES = {"Low", "Medium", "High"}


def _generate_complaint_id():
    """Generate a unique complaint ID in CMP-YYYYMMDD-NNNN format."""
    today = datetime.utcnow()
    prefix = f"CMP-{today.strftime('%Y%m%d')}-"

    latest = (
        Complaint.query.filter(Complaint.complaint_id.like(f"{prefix}%"))
        .order_by(Complaint.complaint_id.desc())
        .first()
    )

    if latest:
        try:
            sequence = int(latest.complaint_id.split("-")[-1]) + 1
        except (ValueError, IndexError):
            sequence = 1
    else:
        sequence = 1

    return f"{prefix}{sequence:04d}"


@complaints_bp.route("", methods=["POST"])
def create_complaint():
    """Create a new complaint with auto-generated ID and default status."""
    data = request.get_json(silent=True) or {}

    animal_id = (data.get("animal_id") or "").strip()
    symptoms = (data.get("symptoms") or "").strip()
    ai_prediction = (data.get("ai_prediction") or "").strip()
    priority = (data.get("priority") or "").strip()

    if not all([animal_id, symptoms, ai_prediction, priority]):
        return jsonify({
            "error": "animal_id, symptoms, ai_prediction, and priority are required",
        }), 400

    if priority not in VALID_PRIORITIES:
        return jsonify({
            "error": "Invalid priority",
            "valid_priorities": sorted(VALID_PRIORITIES),
        }), 400

    if data.get("confidence") is None:
        return jsonify({"error": "confidence is required"}), 400

    try:
        confidence = float(data["confidence"])
    except (TypeError, ValueError):
        return jsonify({"error": "confidence must be a number"}), 400

    animal = Animal.query.get(animal_id)
    if not animal:
        return jsonify({"error": "Animal not found"}), 404

    complaint = Complaint(
        complaint_id=_generate_complaint_id(),
        animal_id=animal_id,
        symptoms=symptoms,
        ai_prediction=ai_prediction,
        confidence=confidence,
        priority=priority,
        status="Submitted",
        complaint_date=date.today(),
    )

    db.session.add(complaint)
    db.session.commit()

    return jsonify({
        "message": "Complaint submitted successfully",
        "data": complaint.to_dict(include_animal=True),
    }), 201


@complaints_bp.route("", methods=["GET"])
def list_complaints():
    """Return all complaints ordered by most recent first."""
    complaints = Complaint.query.order_by(Complaint.complaint_date.desc()).all()
    return jsonify({
        "count": len(complaints),
        "data": [complaint.to_dict(include_animal=True) for complaint in complaints],
    }), 200


@complaints_bp.route("/<complaint_id>", methods=["GET"])
def get_complaint(complaint_id):
    """Return details for a single complaint."""
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404
    return jsonify({"data": complaint.to_dict(include_animal=True)}), 200


@complaints_bp.route("/<complaint_id>/status", methods=["PATCH"])
def update_complaint_status(complaint_id):
    """Update complaint workflow status."""
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404

    data = request.get_json(silent=True) or {}
    new_status = (data.get("status") or "").strip()

    if not new_status:
        return jsonify({"error": "status is required"}), 400

    if new_status not in VALID_STATUSES:
        return jsonify({
            "error": "Invalid status",
            "valid_statuses": sorted(VALID_STATUSES),
        }), 400

    complaint.status = new_status
    db.session.commit()

    return jsonify({
        "message": "Complaint status updated",
        "data": complaint.to_dict(include_animal=True),
    }), 200

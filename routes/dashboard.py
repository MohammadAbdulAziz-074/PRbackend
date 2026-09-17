from flask import Blueprint, jsonify
from sqlalchemy import func

from database import db
from models import Animal, Complaint, Farmer

dashboard_bp = Blueprint("dashboard", __name__)


def _is_healthy(status):
    """Check if animal status is Healthy."""
    return status == "Healthy"


def _is_under_treatment(status):
    """Check if animal status is Under Treatment."""
    return status == "Under Treatment"


@dashboard_bp.route("/summary", methods=["GET"])
def dashboard_summary():
    """Return high-level counts for the admin dashboard."""
    total_farmers = Farmer.query.count()
    total_animals = Animal.query.count()

    animals = Animal.query.with_entities(Animal.status).all()
    healthy_animals = sum(1 for (status,) in animals if _is_healthy(status))
    under_treatment = sum(1 for (status,) in animals if _is_under_treatment(status))

    active_complaints = Complaint.query.filter(Complaint.status != "Recovered").count()
    recovered_cases = Complaint.query.filter_by(status="Recovered").count()

    return jsonify({
        "data": {
            "total_farmers": total_farmers,
            "total_animals": total_animals,
            "healthy_animals": healthy_animals,
            "under_treatment": under_treatment,
            "active_complaints": active_complaints,
            "recovered_cases": recovered_cases,
        }
    }), 200


@dashboard_bp.route("/species", methods=["GET"])
def dashboard_species():
    """Return animal count grouped by species."""
    rows = (
        db.session.query(Animal.species, func.count(Animal.animal_id))
        .group_by(Animal.species)
        .order_by(func.count(Animal.animal_id).desc())
        .all()
    )

    return jsonify({
        "data": [
            {"species": species or "Unknown", "count": count}
            for species, count in rows
        ]
    }), 200


@dashboard_bp.route("/districts", methods=["GET"])
def dashboard_districts():
    """Return farmer count grouped by district."""
    rows = (
        db.session.query(Farmer.district, func.count(Farmer.owner_id))
        .group_by(Farmer.district)
        .order_by(func.count(Farmer.owner_id).desc())
        .all()
    )

    return jsonify({
        "data": [
            {"district": district or "Unknown", "count": count}
            for district, count in rows
        ]
    }), 200

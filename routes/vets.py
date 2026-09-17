from flask import Blueprint, jsonify

from database import db
from models import Animal, Complaint, Farmer


vets_bp = Blueprint("vets", __name__)


@vets_bp.route("/vets/<vet_id>/cases", methods=["GET"])
def get_vet_cases(vet_id):
    cases = (
        db.session.query(Complaint, Animal, Farmer)
        .join(Animal, Complaint.animal_id == Animal.animal_id)
        .join(Farmer, Animal.owner_id == Farmer.owner_id)
        .filter(Complaint.vet_id == vet_id)
        .order_by(Complaint.complaint_date.desc())
        .all()
    )

    return jsonify({
        "count": len(cases),
        "data": [
            {
                "complaint_id": complaint.complaint_id,
                "animal_id": animal.animal_id,
                "animal_name": animal.animal_name,
                "farmer_name": farmer.full_name,
                "ai_prediction": complaint.ai_prediction,
                "priority": complaint.priority,
                "status": complaint.status,
                "complaint_date": (
                    complaint.complaint_date.isoformat()
                    if complaint.complaint_date else None
                ),
            }
            for complaint, animal, farmer in cases
        ],
    }), 200

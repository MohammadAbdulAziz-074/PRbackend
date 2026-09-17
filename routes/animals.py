from flask import Blueprint, jsonify

from models import Animal, HealthRecord, LabReport, Vaccination

animals_bp = Blueprint("animals", __name__)


@animals_bp.route("/animals", methods=["GET"])
def get_animals():
    """Return all animals."""
    animals = Animal.query.all()
    return jsonify({
        "count": len(animals),
        "data": [animal.to_dict() for animal in animals],
    }), 200


@animals_bp.route("/animals/<string:animal_id>", methods=["GET"])
def get_animal(animal_id):
    """Return complete animal profile including owner details."""
    animal = Animal.query.get(animal_id)
    if not animal:
        return jsonify({"error": "Animal not found"}), 404
    return jsonify({"data": animal.to_dict(include_owner=True)}), 200


@animals_bp.route("/animals/<string:animal_id>/vaccinations", methods=["GET"])
def get_animal_vaccinations(animal_id):
    """Return vaccination history for an animal."""
    animal = Animal.query.get(animal_id)
    if not animal:
        return jsonify({"error": "Animal not found"}), 404

    vaccinations = (
        Vaccination.query.filter_by(animal_id=animal_id)
        .order_by(Vaccination.vaccination_date.desc())
        .all()
    )
    return jsonify({
        "animal_id": animal_id,
        "count": len(vaccinations),
        "data": [record.to_dict() for record in vaccinations],
    }), 200


@animals_bp.route("/animals/<string:animal_id>/health", methods=["GET"])
def get_animal_health(animal_id):
    """Return disease / health history for an animal."""
    animal = Animal.query.get(animal_id)
    if not animal:
        return jsonify({"error": "Animal not found"}), 404

    records = (
        HealthRecord.query.filter_by(animal_id=animal_id)
        .order_by(HealthRecord.visit_date.desc())
        .all()
    )
    return jsonify({
        "animal_id": animal_id,
        "count": len(records),
        "data": [record.to_dict() for record in records],
    }), 200


@animals_bp.route("/animals/<string:animal_id>/lab-reports", methods=["GET"])
def get_animal_lab_reports(animal_id):
    """Return laboratory reports for an animal."""
    animal = Animal.query.get(animal_id)
    if not animal:
        return jsonify({"error": "Animal not found"}), 404

    reports = (
        LabReport.query.filter_by(animal_id=animal_id)
        .order_by(LabReport.report_date.desc())
        .all()
    )
    return jsonify({
        "animal_id": animal_id,
        "count": len(reports),
        "data": [report.to_dict() for report in reports],
    }), 200

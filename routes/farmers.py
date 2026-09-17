from flask import Blueprint, jsonify

from models import Animal, Farmer

farmers_bp = Blueprint("farmers", __name__)


@farmers_bp.route("/<int:owner_id>", methods=["GET"])
def get_farmer(owner_id):
    """Return farmer details by owner_id."""
    farmer = Farmer.query.get(owner_id)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404
    return jsonify({"data": farmer.to_dict()}), 200


@farmers_bp.route("/<int:owner_id>/animals", methods=["GET"])
def get_farmer_animals(owner_id):
    """Return all animals belonging to a farmer."""
    farmer = Farmer.query.get(owner_id)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    animals = Animal.query.filter_by(owner_id=owner_id).all()
    return jsonify({
        "owner_id": owner_id,
        "count": len(animals),
        "data": [animal.to_dict() for animal in animals],
    }), 200

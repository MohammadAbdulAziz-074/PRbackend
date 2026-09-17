from flask import Blueprint, jsonify, request

from models import Farmer, Vet

auth_bp = Blueprint("auth", __name__)

VALID_ROLES = {"farmer", "vet", "admin"}
ADMIN_DEMO_ID = "ADMIN01"


@auth_bp.route("/auth/login", methods=["POST"])
def farmer_login():
    """Authenticate a farmer using the registered owner ID and mobile number."""
    data = request.get_json(silent=True) or {}
    owner_id = data.get("owner_id")
    mobile = data.get("mobile")

    if owner_id is None or mobile is None:
        return jsonify({
            "success": False,
            "message": "owner_id and mobile are required",
        }), 400

    try:
        owner_id = int(owner_id)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "owner_id must be a valid integer",
        }), 400

    mobile = str(mobile).strip()
    if not mobile:
        return jsonify({
            "success": False,
            "message": "mobile must not be empty",
        }), 400

    farmer = Farmer.query.filter_by(owner_id=owner_id, mobile=mobile).first()
    if not farmer:
        return jsonify({
            "success": False,
            "message": "Invalid Owner ID or Mobile Number",
        }), 401

    farmer_data = farmer.to_dict()
    return jsonify({
        "success": True,
        "message": "Login successful",
        "farmer": {
            "owner_id": farmer_data["owner_id"],
            "full_name": farmer_data["full_name"],
            "mobile": farmer_data["mobile"],
            "village": farmer_data["village"],
            "district": farmer_data["district"],
        },
    }), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate users by role:
    - farmer: owner_id must exist in farmers table
    - vet: owner_id is treated as vet_id and must exist in vets table
    - admin: demo login with ADMIN01
    """
    data = request.get_json(silent=True) or {}
    user_id = (data.get("owner_id") or "").strip()
    role = (data.get("role") or "").strip().lower()

    if not user_id or not role:
        return jsonify({"error": "owner_id and role are required"}), 400

    if role not in VALID_ROLES:
        return jsonify({"error": f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}"}), 400

    if role == "admin":
        if user_id.upper() != ADMIN_DEMO_ID:
            return jsonify({"error": "Invalid admin credentials. Use ADMIN01 for demo login."}), 401
        profile = {
            "owner_id": ADMIN_DEMO_ID,
            "name": "System Administrator",
            "role": "admin",
        }
        return jsonify({"message": "Login successful", "role": "admin", "profile": profile}), 200

    if role == "farmer":
        try:
            owner_id = int(user_id)
        except ValueError:
            return jsonify({"error": "owner_id must be a valid integer for farmer login"}), 400

        farmer = Farmer.query.get(owner_id)
        if not farmer:
            return jsonify({"error": "Farmer not found with the given owner_id"}), 404
        profile = farmer.to_dict()
        profile["role"] = "farmer"
        return jsonify({"message": "Login successful", "role": "farmer", "profile": profile}), 200

    # role == "vet"
    vet = Vet.query.get(user_id)
    if not vet:
        return jsonify({"error": "Vet not found with the given vet_id"}), 404
    profile = vet.to_dict()
    profile["role"] = "vet"
    return jsonify({"message": "Login successful", "role": "vet", "profile": profile}), 200

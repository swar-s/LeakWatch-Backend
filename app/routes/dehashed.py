
from flask import Blueprint, request, jsonify
from app.services.query_handler import query_dehashed
from app.utils.auth_utils import token_required

dehashed_bp = Blueprint("dehashed", __name__)


@dehashed_bp.route("/", methods=["POST"])
@token_required
def dehashed_lookup():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    result = query_dehashed(email)
    return jsonify(result), 200

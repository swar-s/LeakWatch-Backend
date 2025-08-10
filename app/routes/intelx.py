
from flask import Blueprint, request, jsonify
from app.services.query_handler import query_intelx
from app.utils.auth_utils import token_required

intelx_bp = Blueprint("intelx", __name__)


@intelx_bp.route("/", methods=["POST"])
@token_required
def intelx_lookup():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    result = query_intelx(email)
    return jsonify(result), 200

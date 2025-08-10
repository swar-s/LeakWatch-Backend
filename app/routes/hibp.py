
from flask import Blueprint, request, jsonify
from app.services.query_handler import query_hibp
from app import limiter
from app.utils.auth_utils import token_required

hibp_bp = Blueprint('hibp', __name__)


@hibp_bp.route('/', methods=['POST'])
@limiter.limit("5 per minute")
@token_required
def hibp_lookup():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    result = query_hibp(email)
    return jsonify(result), 200

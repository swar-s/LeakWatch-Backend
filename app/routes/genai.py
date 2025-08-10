
from flask import Blueprint, request, jsonify
from app.services.summarizer import generate_summary
from app.utils.auth_utils import token_required

genai_bp = Blueprint("genai", __name__)


@genai_bp.route("/", methods=["POST"])
@token_required
def summarize_breach():
    data = request.get_json()
    if not data or "breaches" not in data:
        return jsonify({"error": "Breaches data is required"}), 400

    summary = generate_summary(data["breaches"])
    return jsonify({"summary": summary}), 200

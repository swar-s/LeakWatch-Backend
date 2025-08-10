
from flask import Blueprint, request, jsonify
from datetime import datetime
import pytz
from app.utils.db import db
from app.services.query_handler import query_hibp, query_dehashed, query_intelx
from app.services.parser import parse_hibp_response, parse_dehashed_response, parse_intelx_response
from app.utils.helpers import merge_all_parsed
from app.services.summarizer import generate_summary
from app.utils.auth_utils import token_required

scan_bp = Blueprint('scan', __name__)


@scan_bp.route('/', methods=['POST'])
@token_required
def scan_all_sources():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    import logging
    hibp_raw = {}
    dehashed_raw = {}
    intelx_raw = {}
    hibp_parsed = []
    dehashed_parsed = []
    intelx_parsed = []

    try:
        hibp_raw, hibp_status = query_hibp(email)
        print("HIBP raw response:", hibp_raw)
        if "breaches" in hibp_raw:
            hibp_parsed = parse_hibp_response(hibp_raw)
            print("HIBP parsed:", hibp_parsed)
    except Exception as e:
        logging.error(f"HIBP query failed: {e}")
        print(f"HIBP query failed: {e}")

    try:
        dehashed_raw = query_dehashed(email)
        print("DeHashed raw response:", dehashed_raw)
        if "results" in dehashed_raw:
            dehashed_parsed = parse_dehashed_response(dehashed_raw)
            print("DeHashed parsed:", dehashed_parsed)
    except Exception as e:
        logging.error(f"DeHashed query failed: {e}")
        print(f"DeHashed query failed: {e}")

    try:
        intelx_raw = query_intelx(email)
        if isinstance(intelx_raw, tuple):
            intelx_raw, intelx_status = intelx_raw
        print("IntelX raw response:", intelx_raw)
        if "intelx" in intelx_raw:
            intelx_parsed = parse_intelx_response(intelx_raw["intelx"])
            print("IntelX parsed:", intelx_parsed)
    except Exception as e:
        logging.error(f"IntelX query failed: {e}")
        print(f"IntelX query failed: {e}")

    all_results = merge_all_parsed(hibp_parsed, dehashed_parsed, intelx_parsed)

    # Trigger GenAI summarization
    genai_summary = None
    try:
        genai_summary = generate_summary(all_results["all_breaches"])
    except Exception as e:
        genai_summary = {"error": f"GenAI summarization failed: {e}"}

    # Save only GenAI output and minimal metadata
    user_id = None
    if hasattr(request, 'user') and request.user.get('user_id'):
        user_id = request.user['user_id']
    ist = pytz.timezone('Asia/Kolkata')
    scan_doc = {
        'user_id': user_id,
        'email': email,
        'timestamp': datetime.now(ist),
        'genai_summary': genai_summary
    }
    result = db.scans.insert_one(scan_doc)

    return jsonify({
        "genai_summary": genai_summary,
        "scan_id": str(result.inserted_id)
    })


# Route to get scan history for logged-in user (only GenAI output and metadata)
@scan_bp.route('/history', methods=['GET'])
@token_required
def get_scan_history():
    user_id = None
    if hasattr(request, 'user') and request.user.get('user_id'):
        user_id = request.user['user_id']
    if not user_id:
        return jsonify({"error": "User not found in token"}), 401
    scans = list(db.scans.find({'user_id': user_id}).sort('timestamp', -1))
    # Convert ObjectId and datetime to string for JSON serialization
    for scan in scans:
        scan['_id'] = str(scan['_id'])
        if 'timestamp' in scan and scan['timestamp']:
            # Convert to IST if not already
            if scan['timestamp'].tzinfo is None:
                ist = pytz.timezone('Asia/Kolkata')
                scan['timestamp'] = ist.localize(scan['timestamp']).isoformat()
            else:
                scan['timestamp'] = scan['timestamp'].astimezone(
                    pytz.timezone('Asia/Kolkata')).isoformat()
        else:
            scan['timestamp'] = ''
    return jsonify({'scans': scans}), 200

# Route to get a single scan by ID


@scan_bp.route('/<scan_id>', methods=['GET'])
@token_required
def get_single_scan(scan_id):
    from bson import ObjectId
    user_id = None
    if hasattr(request, 'user') and request.user.get('user_id'):
        user_id = request.user['user_id']
    if not user_id:
        return jsonify({"error": "User not found in token"}), 401
    scan = db.scans.find_one({'_id': ObjectId(scan_id), 'user_id': user_id})
    if not scan:
        return jsonify({"error": "Scan not found"}), 404
    scan['_id'] = str(scan['_id'])
    if 'timestamp' in scan and scan['timestamp']:
        if scan['timestamp'].tzinfo is None:
            ist = pytz.timezone('Asia/Kolkata')
            scan['timestamp'] = ist.localize(scan['timestamp']).isoformat()
        else:
            scan['timestamp'] = scan['timestamp'].astimezone(
                pytz.timezone('Asia/Kolkata')).isoformat()
    else:
        scan['timestamp'] = ''
    return jsonify({'scan': scan}), 200

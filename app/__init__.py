from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask_cors import CORS


limiter = Limiter(get_remote_address)


def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app)  # Enable CORS for all domains by default
    app.config.from_object("app.config.Config")

    limiter.init_app(app)

    @limiter.request_filter
    def exempt_health_check():
        return request.path == "/"

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "Rate limit exceeded. Max 5 requests per minute allowed for HIBP lookup."
        }), 429

    # Register blueprints
    from app.routes import register_routes
    register_routes(app)

    return app

    # Expose app instance for Gunicorn
    app = create_app()

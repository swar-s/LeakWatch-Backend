
from flask import Blueprint
from app.routes.hibp import hibp_bp
from app.routes.dehashed import dehashed_bp
from app.routes.intelx import intelx_bp
from app.routes.genai import genai_bp
from app.routes.scan import scan_bp
from app.routes.auth import auth_bp


def register_routes(app):
    app.register_blueprint(hibp_bp, url_prefix='/api/hibp')
    app.register_blueprint(dehashed_bp, url_prefix='/api/dehashed')
    app.register_blueprint(intelx_bp, url_prefix='/api/intelx')
    app.register_blueprint(genai_bp, url_prefix='/api/genai')
    app.register_blueprint(scan_bp, url_prefix='/api/scan')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

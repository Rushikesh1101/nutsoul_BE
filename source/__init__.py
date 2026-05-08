import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from source.routes.logger_config import setup_logger

from source.routes.auth.routes import auth_bp
from source.routes.admin_pages.add_products import admin_pages
from source.routes.admin_pages.admin_routes import admin_routes
from source.routes.cart.cart import cart_routes
from source.routes.user_pages.add_address import add_address_routes
from source.routes.cart.order_routes import ordered_routes

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-prod")
    MONGO_URI = os.getenv("MONGO_URI")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB upload cap


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Vercel serverless: /tmp is the only writable path and is ephemeral.
    app.config["UPLOAD_FOLDER"] = "/tmp/uploads"

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Comma-separated list of allowed origins, e.g.
    # CORS_ORIGINS="https://nutsoul-fe.vercel.app,https://nutsoul.example.com"
    cors_origins = os.getenv("CORS_ORIGINS", "*")
    origins = [o.strip() for o in cors_origins.split(",")] if cors_origins != "*" else "*"
    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)

    JWTManager(app)

    app.logger = setup_logger()

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(admin_pages, url_prefix="/api")
    app.register_blueprint(admin_routes, url_prefix="/api")
    app.register_blueprint(cart_routes, url_prefix="/api")
    app.register_blueprint(add_address_routes, url_prefix="/api")
    app.register_blueprint(ordered_routes, url_prefix="/api")

    @app.route("/")
    def root():
        return jsonify({"status": "ok", "service": "nutsoul-backend"}), 200

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from source.models.model import MongoDB
from source.routes.logger_config import setup_logger

from source.routes.auth.routes import auth_bp
from source.routes.admin_pages.add_products import admin_pages
from source.routes.admin_pages.admin_routes import admin_routes
from source.routes.cart.cart import cart_routes
from source.routes.user_pages.add_address import add_address_routes
from source.routes.cart.order_routes import ordered_routes

load_dotenv()

mongo = MongoDB()

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    CORS(app)

    JWTManager(app)

    logger = setup_logger()
    app.logger = logger

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(admin_pages, url_prefix="/api")
    app.register_blueprint(admin_routes, url_prefix="/api")
    app.register_blueprint(cart_routes, url_prefix="/api")
    app.register_blueprint(add_address_routes, url_prefix="/api")
    app.register_blueprint(ordered_routes, url_prefix="/api")

    @app.teardown_appcontext
    def close_db(exception=None):
        mongo.close()

    return app

from flask import Flask
from flask_cors import CORS
from source.routes.auth.routes import auth_bp
from source.routes.admin_pages.add_products import admin_pages
from source.routes.admin_pages.admin_routes import admin_routes
from source.routes.cart.cart import cart_routes
from source.routes.user_pages.add_address import add_address_routes
from source.routes.cart.order_routes import ordered_routes
from source.models.model import MongoDB
from flask_jwt_extended import JWTManager
import os

from dotenv import load_dotenv

load_dotenv()

from source.routes.logger_config import setup_logger

mongo = MongoDB()

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")


def create_app():

    products_folder = os.path.join(os.getcwd(), "products")

    app = Flask(__name__, static_folder=products_folder, static_url_path="/products")

    # app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # Add these session configurations
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production with HTTPS
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    CORS(app)
    app.config.from_object(Config)
    jwt = JWTManager(app)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # logger setup
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

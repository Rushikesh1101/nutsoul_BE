import base64
from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
from source.models.model import MongoDB

mongo = MongoDB()

admin_pages = Blueprint("admin_pages", __name__, url_prefix="/api")


@admin_pages.route("/add_products", methods=["POST"])
def add_items():
    try:
        items_collection = mongo.db["items"]

        data = request.form.to_dict()

        image = request.files.get("image")
        if not image:
            return jsonify({"status": False, "message": "Image is required"}), 400

        in_stock_value = data.get("in_stock", "true").lower()
        data["in_stock"] = True if in_stock_value == "true" else False

        filename = secure_filename(image.filename or "image")
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"

        image_bytes = image.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        mimetype = image.mimetype or "image/jpeg"

        data["image_filename"] = filename
        data["image_mimetype"] = mimetype
        data["image_b64"] = image_b64

        numeric_fields = [
            "price_100g",
            "price_250g",
            "price_500g",
            "price_1kg",
        ]
        for field in numeric_fields:
            if field in data:
                data[field] = str(data[field])

        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()

        result = items_collection.insert_one(data)

        return jsonify({
            "status": True,
            "message": "Item added successfully",
            "inserted_id": str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({
            "status": False,
            "message": str(e)
        }), 500

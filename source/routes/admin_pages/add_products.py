import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
from source.models.model import MongoDB

mongo = MongoDB()

admin_pages = Blueprint("admin_pages", __name__, url_prefix="/api")

UPLOAD_FOLDER = "products"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@admin_pages.route("/add_products", methods=["POST"])
def add_items():
    try:
        items_collection = mongo.db["items"]

        # Get form fields
        data = request.form.to_dict()

        # Get image file
        image = request.files.get("image")

        if not image:
            return jsonify({"status": False, "message": "Image is required"}), 400
        
        in_stock_value = data.get("in_stock", "true").lower()
        data["in_stock"] = True if in_stock_value == "true" else False
        # Secure filename
        filename = secure_filename(image.filename)

        # Add timestamp to filename (avoid duplicate)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"

        image_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save image
        image.save(image_path)

        # Store image path in DB
        data["image_path"] = image_path

        # Convert numeric values to string
        numeric_fields = [
            "price_100g",
            "price_250g",
            "price_500g",
            "price_1kg",
        ]

        for field in numeric_fields:
            if field in data:
                data[field] = str(data[field])

        # Add timestamps
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()

        # Insert into MongoDB
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
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from models.user import db
from models.abr import Abr   # ✅ updated import
import string
import random

admin_activities = Blueprint('admin_activities', __name__)

def generate_abr_id():
    return 'ABR-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# ✅ CREATE activity
@admin_activities.route("/api/admin/activities", methods=["POST"])
@cross_origin()
def create_activity():
    data = request.get_json()
    try:
        raw_rate = str(data.get('rate', 0))
        numeric_rate = float(
            ''.join(filter(lambda x: x.isdigit() or x == '.', raw_rate))
        )

        new_activity = Abr(
            abr_id=generate_abr_id(),
            name=data.get('name'),
            applies_to=data.get('appliesTo'),
            # If your Database model HAS a 'rule' column that is NOT NULL, 
            # pass an empty string or "fixed" here to satisfy the DB.
            rule=data.get('rule', ''), 
            rate=numeric_rate,
            from_date=data.get('effectiveFrom'),
            created_by=data.get('admin_id', 'ADMIN-01')
        )

        db.session.add(new_activity)
        db.session.commit()

        return jsonify(new_activity.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        # This will now show the actual DB error in your Render logs
        print(f"Error creating activity: {str(e)}") 
        return jsonify({"error": str(e)}), 500


@admin_activities.route(
    "/api/admin/activities/delete/<string:abr_id>",
    methods=["DELETE", "OPTIONS"]
)
@cross_origin()
def delete_activity(abr_id):

    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    activity = Abr.query.filter_by(abr_id=abr_id).first()

    if not activity:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(activity)
    db.session.commit()

    return jsonify({
        "message": "Deleted successfully",
        "abr_id": abr_id
    }), 200

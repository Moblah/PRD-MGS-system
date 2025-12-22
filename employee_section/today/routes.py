from flask import Blueprint, request, jsonify
from models.user import db
from models.activity import Activity
import string
import random

employee_today = Blueprint('employee_today', __name__)

@employee_today.route("/api/abr", methods=["GET"])
def get_abr_data():
    """Get all activities and rates from ABR table"""
    try:
        # Query all data from ABR table
        abr_data = ABR.query.all()
        
        # Convert to list of dictionaries
        result = []
        for item in abr_data:
            result.append({
                'name': item.name,
                'rate': float(item.rate),
                'applies_to': item.applies_to,
                'rule': item.rule  # Include rule if needed
            })
        
        print(f"✅ Returning {len(result)} ABR records")
        print(f"📝 First record: {result[0] if result else 'No data'}")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error in /api/abr: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
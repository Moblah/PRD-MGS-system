from flask import Blueprint, request, jsonify
from models.user import db
from models.activity import Activity
import string
import random

employee_today = Blueprint('employee_today', __name__)

@employee_today.route("/api/abr", methods=["GET"])
def get_abr_data():
    """Get all activities and rates from ABR table"""
    print("🔍 /api/abr endpoint called - checking database...")
    
    try:
        # Check if we can import the model
        print("🔍 Importing ABR model...")
        from models.abr import ABR
        
        # Test the query
        print("🔍 Executing database query...")
        count = ABR.query.count()
        print(f"🔍 Found {count} records in ABR table")
        
        if count == 0:
            print("⚠️ ABR table is empty!")
            return jsonify([]), 200
        
        # Get all data
        abr_data = ABR.query.all()
        print(f"🔍 Retrieved {len(abr_data)} records")
        
        # Convert to JSON
        result = []
        for i, item in enumerate(abr_data):
            result.append({
                'name': item.name,
                'rate': float(item.rate),
                'applies_to': item.applies_to,
                'rule': item.rule
            })
            
            # Log first 3 records
            if i < 3:
                print(f"📝 Record {i+1}: {item.name} - {item.rate} - {item.applies_to}")
        
        print(f"✅ Returning {len(result)} ABR records")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in /api/abr: {type(e).__name__}: {str(e)}")
        import traceback
        print("Stack trace:")
        traceback.print_exc()
        
        # Return empty array so frontend doesn't crash
        return jsonify([]), 200
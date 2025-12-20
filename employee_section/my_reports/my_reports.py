from flask import Blueprint, jsonify
from flask_cors import cross_origin
from models.user import db
from models.activity import Activity
from models.abr import Abr  # ✅ Use the new Abr model instead of Oparations

my_reports_bp = Blueprint("my_reports_bp", __name__)

# ✅ Now use it as a decorator
@my_reports_bp.route("/api/employee/reports/<user_alnum>", methods=["GET"])
@cross_origin()
def get_employee_reports(user_alnum):
    try:
        print(f"Fetching reports for user: {user_alnum}")
        
        # Simple query without join first for debugging
        activities = Activity.query.filter_by(created_by=user_alnum)\
            .order_by(Activity.time_date.desc()).all()
        
        print(f"Found {len(activities)} activities")
        
        reports = []
        for act in activities:
            # Try to get Abr info
            abr_info = Abr.query.filter_by(name=act.activity).first()
            applies_to = abr_info.applies_to if abr_info else "Unknown"
            
            reports.append({
                "id": act.id,
                "date": act.time_date.strftime('%Y-%m-%d') if act.time_date else "N/A",
                "activity_name": act.activity,
                "roleType": applies_to,
                "totalBonus": float(act.amount) if act.amount is not None else 0.0,
                "status": "Submitted",
                "statusColor": "text-green-600",
                "bgColor": "bg-green-50"
            })
        
        print(f"Returning {len(reports)} reports")
        return jsonify(reports), 200
        
    except Exception as e:
        print(f"ERROR fetching reports for {user_alnum}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500
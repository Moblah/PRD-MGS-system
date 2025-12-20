from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from datetime import datetime, date, timedelta
from models.user import db, User
from models.activity import Activity
from models.abr import Abr
from sqlalchemy import func

admin_dashboard_bp = Blueprint("admin_dashboard_bp", __name__)

@admin_dashboard_bp.route("/api/admin/dashboard", methods=["GET"])
@cross_origin()
def get_admin_dashboard():
    try:
        # Get date parameter (default to today)
        selected_date = request.args.get('date', date.today().isoformat())
        
        # Parse date
        try:
            filter_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            filter_date = date.today()
        
        print(f"Fetching dashboard data for date: {filter_date}")

        # ===== 1. REPORTS SUBMITTED TODAY =====
        reports_today = db.session.query(Activity).filter(
            func.date(Activity.time_date) == filter_date
        ).count()

        # ===== 2. GET ALL EMPLOYEES =====
        all_employees = User.query.filter(
            func.lower(User.role) == "employee"
        ).all()
        employee_count = len(all_employees)
        
        # ===== 3. GET EMPLOYEES WHO SUBMITTED TODAY =====
        submitted_today = db.session.query(Activity.created_by).filter(
            func.date(Activity.time_date) == filter_date
        ).distinct().all()
        submitted_employee_ids = [emp[0] for emp in submitted_today]
        
        # ===== 4. CALCULATE MISSING REPORTS =====
        missing_reports = employee_count - len(submitted_employee_ids)

        # ===== 5. TODAY'S BONUS TOTAL =====
        # Calculate total bonus from ALL activities for the selected date
        today_bonus_result = db.session.query(
            func.sum(Activity.amount)
        ).filter(
            func.date(Activity.time_date) == filter_date
        ).first()
        today_bonus_total = float(today_bonus_result[0]) if today_bonus_result[0] else 0.0

        # ===== 6. RECENT SUBMISSIONS =====
        recent_submissions_query = db.session.query(
            Activity.time_date,
            Activity.activity,
            Activity.qty,
            Activity.amount,
            User.name,
            Abr.applies_to
        ).join(
            User, Activity.created_by == User.user_alnum
        ).outerjoin(
            Abr, Activity.activity == Abr.name
        ).filter(
            func.date(Activity.time_date) == filter_date
        ).order_by(Activity.time_date.desc()).limit(10).all()

        recent_submissions = []
        for sub in recent_submissions_query:
            recent_submissions.append({
                "time": sub.time_date.strftime('%H:%M') if sub.time_date else "",
                "employee": sub.name,
                "date": sub.time_date.strftime('%m-%d') if sub.time_date else "",
                "roleType": sub.applies_to if sub.applies_to else "Unknown",
                "items": int(sub.qty) if sub.qty else 0,
                "total": f" {sub.amount:,.0f}" if sub.amount else "0"
            })

        # ===== 7. MISSING REPORTS DETAILS =====
        missing_employees = []
        for employee in all_employees:
            if employee.user_alnum not in submitted_employee_ids:
                missing_employees.append({
                    "user_alnum": employee.user_alnum,
                    "name": employee.name,
                    "team": employee.team
                })

        # ===== 8. YESTERDAY'S COMPARISON =====
        yesterday = filter_date - timedelta(days=1)
        yesterday_reports = db.session.query(Activity).filter(
            func.date(Activity.time_date) == yesterday
        ).count()
        
        yesterday_bonus_result = db.session.query(
            func.sum(Activity.amount)
        ).filter(
            func.date(Activity.time_date) == yesterday
        ).first()
        yesterday_bonus = float(yesterday_bonus_result[0]) if yesterday_bonus_result[0] else 0.0

        return jsonify({
            "stats": {
                "reportsSubmittedToday": reports_today,
                "missingReportsToday": missing_reports,
                "mtdBonusTotal": today_bonus_total,  # This now shows TODAY's total bonus
                "totalEmployees": employee_count,
                "yesterdayComparison": {
                    "reports": yesterday_reports,
                    "bonus": yesterday_bonus
                }
            },
            "recentSubmissions": recent_submissions,
            "missingEmployees": missing_employees,
            "selectedDate": filter_date.isoformat(),
            "today": date.today().isoformat()
        }), 200

    except Exception as e:
        print(f"Error fetching admin dashboard data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500
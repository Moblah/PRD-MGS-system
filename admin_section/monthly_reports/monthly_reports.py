from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from datetime import datetime, date, timedelta
from models.user import db, User
from models.activity import Activity
from models.abr import Abr
from sqlalchemy import func, extract
import calendar
from sqlalchemy import func, extract, case, and_, or_
from sqlalchemy.orm import aliased

import traceback



monthly_reports_bp = Blueprint('monthly_reports_bp', __name__)



# Test endpoint - Add FULL PATH like your working blueprint
@monthly_reports_bp.route("/api/admin/monthly-reports/test", methods=["GET"])
@cross_origin()
def test_endpoint():
    """Simple test endpoint to verify API is working"""
    return jsonify({
        "success": True,
        "message": "Monthly Reports API is working!",
        "timestamp": datetime.now().isoformat()
    }), 200

# Get available months - Add FULL PATH
@monthly_reports_bp.route("/api/admin/monthly-reports/months", methods=["GET"])
@cross_origin()
def get_available_months():
    try:
        # Get unique months from activities
        months_data = db.session.query(
            extract('year', Activity.time_date),
            extract('month', Activity.time_date)
        ).distinct().filter(
            Activity.time_date.isnot(None)
        ).all()
        
        months_list = []
        for year, month in months_data:
            if year and month:
                month_name = calendar.month_name[int(month)]
                months_list.append(f"{month_name} {int(year)}")
        
        # If no months, use current and previous
        if not months_list:
            current = datetime.now()
            prev = current.replace(day=1) - timedelta(days=1)
            months_list = [
                f"{current.strftime('%B')} {current.year}",
                f"{prev.strftime('%B')} {prev.year}"
            ]
        
        return jsonify({"months": months_list, "success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# Get monthly report - Add FULL PATH
@monthly_reports_bp.route("/api/admin/monthly-reports/report", methods=["GET"])
@cross_origin()
def get_monthly_report():
    try:
        month_year = request.args.get('month', '')
        team_filter = request.args.get('team', 'All')
        status_filter = request.args.get('status', 'Submitted')
        
        if not month_year:
            return jsonify({"error": "Month required", "success": False}), 400
        
        # Parse month
        month_name, year = month_year.split(' ')
        month_num = list(calendar.month_name).index(month_name)
        year = int(year)
        
        # Get date range
        _, last_day = calendar.monthrange(year, month_num)
        start = datetime(year, month_num, 1)
        end = datetime(year, month_num, last_day, 23, 59, 59)
        
        # Get employees
        employees = User.query.filter(User.role.ilike('%employee%')).all()
        
        report_data = []
        for user in employees:
            if team_filter != 'All' and user.team != team_filter:
                continue
            
            # Count distinct days with activities
            distinct_days = db.session.query(
                func.date(Activity.time_date)
            ).filter(
                Activity.created_by == user.user_alnum,
                Activity.time_date >= start,
                Activity.time_date <= end
            ).distinct().count()
            
            # Get total bonus
            total_bonus_result = db.session.query(
                func.sum(Activity.amount)
            ).filter(
                Activity.created_by == user.user_alnum,
                Activity.time_date >= start,
                Activity.time_date <= end
            ).first()
            
            total_bonus = float(total_bonus_result[0] or 0)
            
            # Apply status filter
            if status_filter != 'All':
                if status_filter == 'Submitted' and distinct_days == 0:
                    continue
                elif status_filter == 'Pending' and distinct_days > 0:
                    continue
            
            # Calculate exceptions
            days_without = last_day - distinct_days
            exceptions = "—"
            if days_without > 0:
                exceptions = f"{days_without} missing days"
            
            status = "Submitted" if distinct_days > 0 else "Not Submitted"
            
            report_data.append({
                "id": user.id,
                "employee": user.name,
                "employee_alnum": user.user_alnum,
                "days": distinct_days,
                "totalBonus": f"{total_bonus:,.2f}",
                "bonus_numeric": total_bonus,
                "exceptions": exceptions,
                "exceptions_count": days_without,
                "status": status,
                "team": user.team or "Not Assigned"
            })
        
        # Summary stats
        total_emp = len(report_data)
        total_days = sum(e['days'] for e in report_data)
        with_exceptions = sum(1 for e in report_data if e['exceptions_count'] > 0)
        total_bonus_all = sum(e['bonus_numeric'] for e in report_data)
        avg_days = round(total_days / total_emp) if total_emp > 0 else 0
        
        return jsonify({
            "success": True,
            "report": report_data,
            "month": month_year,
            "summary": {
                "total_employees": total_emp,
                "total_days": total_days,
                "employees_with_exceptions": with_exceptions,
                "total_bonus": total_bonus_all,
                "average_days": avg_days
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# Get employee details - Add FULL PATH
@monthly_reports_bp.route("/api/admin/monthly-reports/employee-details/<user_alnum>", methods=["GET"])
@cross_origin()
def get_employee_monthly_details(user_alnum):
    try:
        month_year = request.args.get('month', '')
        
        if not month_year:
            return jsonify({"error": "Month required", "success": False}), 400
        
        month_name, year = month_year.split(' ')
        month_num = list(calendar.month_name).index(month_name)
        year = int(year)
        
        _, last_day = calendar.monthrange(year, month_num)
        start = datetime(year, month_num, 1)
        end = datetime(year, month_num, last_day, 23, 59, 59)
        
        user = User.query.filter_by(user_alnum=user_alnum).first()
        if not user:
            return jsonify({"error": "Employee not found", "success": False}), 404
        
        # Get activities grouped by date
        daily_data = db.session.query(
            func.date(Activity.time_date),
            func.count(Activity.id),
            func.sum(Activity.amount)
        ).filter(
            Activity.created_by == user_alnum,
            Activity.time_date >= start,
            Activity.time_date <= end
        ).group_by(func.date(Activity.time_date)).all()
        
        all_activities = Activity.query.filter(
            Activity.created_by == user_alnum,
            Activity.time_date >= start,
            Activity.time_date <= end
        ).all()
        
        return jsonify({
            "success": True,
            "employee": {
                "name": user.name,
                "team": user.team
            },
            "month": month_year,
            "daily_summary": [
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "activity_count": count,
                    "daily_total": float(total or 0)
                }
                for date, count, total in daily_data
            ],
            "activities": [
                {
                    "id": a.id,
                    "activity": a.activity,
                    "qty": float(a.qty or 0),
                    "amount": float(a.amount or 0),
                    "time_date": a.time_date.strftime("%Y-%m-%d %H:%M:%S")
                }
                for a in all_activities
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# Get teams - Add FULL PATH
@monthly_reports_bp.route("/api/admin/monthly-reports/teams", methods=["GET"])
@cross_origin()
def get_teams():
    try:
        teams = db.session.query(User.team).distinct().filter(
            User.team.isnot(None)
        ).all()
        
        teams_list = ["All"] + [t[0] for t in teams if t[0]]
        return jsonify({"teams": teams_list, "success": True}), 200
    except:
        return jsonify({"teams": ["All", "Field", "Office"], "success": True}), 200
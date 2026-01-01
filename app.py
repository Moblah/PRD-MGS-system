from flask import Flask
from flask_cors import CORS
from config import Config
from models.user import db
from models.activity import Activity  # Ensure table creation

# Import Blueprints from respective sections
from login.login import login_bp
from admin_section.users.routes import admin_users
from admin_section.activities.routes import admin_activities
from employee_section.today.routes import employee_today
# New Blueprint for My Reports
from employee_section.my_reports.my_reports import my_reports_bp 
from admin_section.dashboard.admin_dashboard import admin_dashboard_bp
from admin_section.monthly_reports.monthly_reports import monthly_reports_bp
from models.payment import PaymentBatch, PaymentAdjustment # <--- ADD THIS
from admin_section.payments.routes import admin_payments  # <--- ADD THIS

def create_app():
    """
    Factory function to create Flask app------------
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for React <-> Flask communication
    CORS(app)

    # Initialize database
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(login_bp)
    app.register_blueprint(admin_users)      # Admin User Management
    app.register_blueprint(employee_today)   # Employee Daily Activities (Today)
    app.register_blueprint(admin_activities) # Admin Activities Management
    app.register_blueprint(my_reports_bp)    # Employee Performance History (My Reports)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(monthly_reports_bp)
    app.register_blueprint(admin_payments)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app

# Expose app for shell imports
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
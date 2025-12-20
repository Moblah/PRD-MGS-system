import os

class Config:
    # Get Render's PostgreSQL URL, fallback to SQLite for local dev
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
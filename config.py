import os

class Config:
    # Determine if we're on Render (has DATABASE_URL) or local
    if os.environ.get('DATABASE_URL'):
        # On Render - use PostgreSQL
        db_url = os.environ['DATABASE_URL']
        # Fix URL format if needed
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = db_url
        print("📦 Running on Render with PostgreSQL")
    else:
        # Local development - use SQLite (or MySQL if you prefer)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app.db'
        # If you want MySQL locally: 'mysql+pymysql://user:pass@localhost/dbname'
        print("💻 Running locally with SQLite")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Other configs from your working project
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change')
    BCRYPT_LOG_ROUNDS = 12
    
    # Flask-Mail config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Flask-Caching config
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Flask-Limiter config
    RATELIMIT_ENABLED = True

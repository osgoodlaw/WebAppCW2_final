import os

# Flask configuration settings
SECRET_KEY = 'a-very-secret-elephant'  # Secret key for session signing
WTF_CSRF_ENABLED = True  # Enable CSRF protection

# For deployment, use a secure cookie
SESSION_COOKIE_SECURE = False  # Set this to True if deploying over HTTPS

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoid overhead of tracking object changes
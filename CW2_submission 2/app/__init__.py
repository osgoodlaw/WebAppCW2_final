from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object('config')

csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from app.models import User  # Import models after db is initialized

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Ensure User model is imported

# Import views after initializing all extensions
from app import views, models

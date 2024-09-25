from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

""" from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api') """

from app import routes, models
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)
    #from .routes.decision_maker_routes import register_routes
    #register_routes(app)
    return app

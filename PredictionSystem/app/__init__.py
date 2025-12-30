from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
    db.init_app(app)
    # from .routes.order_routes import register_routes
    # register_routes(app)
    with app.app_context():
        db.create_all()
    return app

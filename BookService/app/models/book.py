from flask_sqlalchemy import SQLAlchemy
from app import db
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Book {self.item_name}>'
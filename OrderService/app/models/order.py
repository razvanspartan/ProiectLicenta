from flask_sqlalchemy import SQLAlchemy

db= SQLAlchemy()

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Order {self.item_name}>'
from app import db
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Float, nullable=False)
    books = db.relationship('OrderBook', backref='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.item_name}>'
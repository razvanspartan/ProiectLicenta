from flask import jsonify

from app.models.order import Order
from app.models.order_books import OrderBook


def register_routes(app):
    @app.route('/orders', methods=['GET'])
    def get_orders():
        orders = Order.query.all()
        orders_list = [{'id': order.id,
                        'customer_name': order.customer_name,
                        'total': order.total, 'books':
                            [{'book_id': book.book_id,
                              'quantity': book.quantity,
                              'price': book.price} for book in order.books]}
                       for order in orders]
        return jsonify(orders_list)

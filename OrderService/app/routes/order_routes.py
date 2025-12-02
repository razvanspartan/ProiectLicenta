from flask import jsonify, request

from app.models.order import Order
from app.models.order_books import OrderBook


def register_routes(app):
    from app import db
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

    @app.route('/orders/<int:order_id>', methods=['GET'])
    def get_order(order_id):
        order = Order.query.get_or_404(order_id)
        return jsonify({'id': order.id, 'customer_name': order.customer_name, 'books':
                            [{'book_id': book.book_id,
                              'quantity': book.quantity,
                              'price': book.price} for book in order.books],
                       'total': order.total})

    @app.route('/orders', methods=['POST'])
    def create_order():
        data = request.get_json()
        new_order = Order(customer_name=data['customer_name'], total=data['total'])
        db.session.add(new_order)
        db.session.flush()
        items_data = data.get('items', [])
        for item in items_data:
            order_item = OrderBook(
                order_id=new_order.id,
                book_id=item['book_id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)

        db.session.commit()
        return jsonify({'message': 'order created'}), 201
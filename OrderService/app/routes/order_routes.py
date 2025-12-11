import socket
import threading
import time

import requests
from app.models.order import Order
from app.models.order_books import OrderBook
from flask import jsonify, request


def register_routes(app):
    from app import db
    @app.route('/api/v1/orderservice/orders', methods=['GET'])
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

    @app.route('/api/v1/orderservice/orders/<int:order_id>', methods=['GET'])
    def get_order(order_id):
        order = Order.query.get_or_404(order_id)
        return jsonify({'id': order.id, 'customer_name': order.customer_name, 'books':
            [{'book_id': book.book_id,
              'quantity': book.quantity,
              'price': book.price} for book in order.books],
                        'total': order.total})

    @app.route('/api/v1/orderservice/orders', methods=['POST'])
    def create_order():
        data = request.get_json()
        new_order = Order(customer_name=data['customer_name'], total=data['total'])
        db.session.add(new_order)
        db.session.flush()
        items_data = data.get('books', [])
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

    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)

    @app.route('/api/v1/orderservice/expensive_cpu_computations', methods=['GET'])
    def expensive_cpu_computations():
        result = fib(40)
        return {"fib": result}

    @app.route('/api/v1/orderservice/expensive_memory_usage', methods=['GET'])
    def expensive_memory_usage():
        big_list = [i for i in range(10 ** 7)]
        total = sum(big_list)
        return {"total": total}

    @app.route('/api/v1/orderservice/health', methods=['GET'])
    def health_check():
        print("send heartbeat")
        return "OK", 200

    def register_to_load_balancer():
        while True:
            load_balancer_url = "http://loadbalancer:7000/api/v1/loadbalancer/register"
            data = {
                "service_name": "orderservice",
                "service_ip": socket.gethostbyname(socket.gethostname()),
                "service_port": 4000
            }
            try:
                response = requests.post(load_balancer_url, json=data)
                if response.status_code == 201:
                    print("OrderService instance registered with Load Balancer successfully.")
                else:
                    print("OrderService instance registration with Load Balancer failed.")
            except Exception as e:
                print(f"error registering OrderService instance with Load Balancer: {e}")
            time.sleep(10)
    threading.Thread(target=register_to_load_balancer, daemon=True).start()

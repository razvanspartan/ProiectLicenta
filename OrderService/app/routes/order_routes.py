import threading
import time

from app.models.order import Order
from app.models.order_books import OrderBook
from flask import jsonify, request

from app.services.registration_service import register_to_load_balancer


def register_routes(app):
    from app import db

    @app.route("/api/v1/orderservice/orders", methods=["GET"])
    def get_orders():
        orders = Order.query.all()
        orders_list = [
            {
                "id": order.id,
                "customer_name": order.customer_name,
                "total": order.total,
                "books": [
                    {
                        "book_id": book.book_id,
                        "quantity": book.quantity,
                        "price": book.price,
                    }
                    for book in order.books
                ],
            }
            for order in orders
        ]
        return jsonify(orders_list)

    @app.route("/api/v1/orderservice/orders/<int:order_id>", methods=["GET"])
    def get_order(order_id):
        order = Order.query.get_or_404(order_id)
        return jsonify(
            {
                "id": order.id,
                "customer_name": order.customer_name,
                "books": [
                    {
                        "book_id": book.book_id,
                        "quantity": book.quantity,
                        "price": book.price,
                    }
                    for book in order.books
                ],
                "total": order.total,
            }
        )

    @app.route("/api/v1/orderservice/orders", methods=["POST"])
    def create_order():
        data = request.get_json()
        new_order = Order(customer_name=data["customer_name"], total=data["total"])
        db.session.add(new_order)
        db.session.flush()
        items_data = data.get("books", [])
        for item in items_data:
            order_item = OrderBook(
                order_id=new_order.id,
                book_id=item["book_id"],
                quantity=item["quantity"],
                price=item["price"],
            )
            db.session.add(order_item)

        db.session.commit()
        return jsonify({"message": "order created"}), 201

    @app.route("/api/v1/orderservice/expensive_cpu_computations", methods=["GET"])
    def expensive_cpu_computations():
        start = time.time()
        work_duration = 0.3

        while time.time() - start < work_duration:
            x = 0
            for i in range(10_000):
                x += i * i
            time.sleep(0.001)

        return {"status": "completed", "computation_time": work_duration}

    @app.route("/api/v1/orderservice/expensive_memory_usage", methods=["GET"])
    def expensive_memory_usage():
        big_list = [i for i in range(10**7)]
        total = sum(big_list)
        return {"total": total}

    @app.route("/api/v1/orderservice/health", methods=["GET"])
    def health_check():
        print("send heartbeat")
        return "OK", 200

    threading.Thread(target=register_to_load_balancer, daemon=True).start()

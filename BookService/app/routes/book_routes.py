import os
import threading
import time

from flask import jsonify
from flask import request
import requests
from app.models.book import Book
import socket

def register_routes(app):
    @app.route('/api/v1/bookservice/books', methods=['GET'])
    def get_books():
        print("THis isntance got called:" + socket.gethostbyname(socket.gethostname()))
        books = Book.query.all()
        books_list = [{'id': order.id,
                       'book_title': order.book_title,
                       'author': order.author,
                       'stock': order.stock,
                       'price': order.price}
                      for order in books]
        return jsonify(books_list)

    @app.route('/api/v1/bookservice/<int:book_id>', methods=['GET'])
    def get_book(book_id):
        book = Book.query.get_or_404(book_id)
        return jsonify({'id': book.id,
                        'book_title': book.book_title,
                        'author': book.author,
                        'stock': book.stock,
                        'price': book.price})

    @app.route('/api/v1/bookservice/books', methods=['POST'])
    def create_book():
        data = request.get_json()
        new_book = Book(
            book_title=data['book_title'],
            author=data['author'],
            stock=data['stock'],
            price=data['price']
        )
        from app import db
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'book created'}), 201

    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)

    @app.route('/api/v1/bookservice/expensive_cpu_computations', methods=['GET'])
    def expensive_cpu_computations():
        start = time.time()
        work_duration = 0.3  # Target total time

        while time.time() - start < work_duration:
            # Do some computation
            x = 0
            for i in range(1_000):  # Reduced iterations
                x += i * i

            # Add sleep to yield CPU
            time.sleep(0.001)  # Sleep 1ms between batches

        return {"status": "completed", "computation_time": work_duration}

    @app.route('/api/v1/bookservice/expensive_memory_usage', methods=['GET'])
    def expensive_memory_usage():
        big_list = [i for i in range(10 ** 7)]
        total = sum(big_list)
        return {"total": total}

    @app.route('/api/v1/bookservice/health', methods=['GET'])
    def health_check():
        print("send heartbeat")
        return "OK", 200

    def register_to_load_balancer():
        while True:
            load_balancer_url = "http://loadbalancer:7000/api/v1/loadbalancer/register"
            data = {
                "service_name": "bookservice",
                "service_ip": socket.gethostbyname(socket.gethostname()),
                "service_port": 6000
            }
            try:
                requests.post(load_balancer_url, json=data, timeout=2)
            except Exception as e:
                print(f"Error registering BookService with Load Balancer: {e}")
            time.sleep(5)
    threading.Thread(target=register_to_load_balancer, daemon=True).start()

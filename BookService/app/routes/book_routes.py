from flask import jsonify
from flask import request

from app.models.book import Book


def register_routes(app):
    @app.route('/api/v1/book/books', methods=['GET'])
    def get_books():
        books = Book.query.all()
        books_list = [{'id': order.id,
                       'book_title': order.book_title,
                       'author': order.author,
                       'stock': order.stock,
                       'price': order.price}
                      for order in books]
        return jsonify(books_list)

    @app.route('/api/v1/book/<int:book_id>', methods=['GET'])
    def get_book(book_id):
        book = Book.query.get_or_404(book_id)
        return jsonify({'id': book.id,
                        'book_title': book.book_title,
                        'author': book.author,
                        'stock': book.stock,
                        'price': book.price})

    @app.route('/api/v1/book/books', methods=['POST'])
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

    @app.route('/api/v1/book/expensive_cpu_computations', methods=['GET'])
    def expensive_cpu_computations():
        result = fib(40)
        return {"fib": result}

    @app.route('/api/v1/book/expensive_memory_usage', methods=['GET'])
    def expensive_memory_usage():
        big_list = [i for i in range(10 ** 7)]
        total = sum(big_list)
        return {"total": total}

    @app.route('/api/v1/book/health', methods=['GET'])
    def health_check():
        return "OK", 200

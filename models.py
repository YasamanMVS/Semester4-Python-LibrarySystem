import sqlite3
from datetime import datetime, timedelta

def get_db_connection():
    conn = sqlite3.connect('library_system.db')
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

class Book:
    def __init__(self, title, author, category, quantity = 5):
        self.title = title
        self.author = author
        self.category = category
        self.quantity = quantity
        self.availability = 'yes' if self.quantity > 0 else 'no'

    def save_to_db(self):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO books (title, author, category, quantity, availability)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.title, self.author, self.category, self.quantity, self.availability))
            conn.commit()

    def borrow(self):
        if self.quantity > 0:
            self.quantity -= 1
            self.availability = 'yes' if self.quantity > 0 else 'no'
            self.update_availability()
        else:
            print(f"The book {self.title} is not available for rent.")

    def return_book(self):
        self.quantity += 1
        self.availability = 'yes'
        self.update_availability()

    @staticmethod
    def update_availability(book_id, decrement=False, increment=False):
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT quantity FROM books WHERE id = ?', (book_id,))
            quantity = cursor.fetchone()[0]

            if decrement and quantity > 0:
                quantity -= 1
            elif increment:
                quantity += 1
            availability = 'yes' if quantity > 0 else 'no'

            # Update database
            cursor.execute('''
                UPDATE books SET quantity = ?, availability = ? WHERE id = ?
            ''', (quantity, availability, book_id))
            conn.commit()

    @staticmethod
    def search(search_query):
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM books
        WHERE title LIKE ?
        OR author LIKE ?
        OR category LIKE ?;
        """

        like_query = f"%{search_query}%"
        params = (like_query, like_query, like_query)

        try:
            cursor.execute(query, params)
            books = cursor.fetchall()
            return books
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()

    @staticmethod
    def get_all_books():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books")
            all_books = cursor.fetchall()
            return all_books


class User:
    def __init__(self, name):
        self.name = name

    def save_to_db(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name) VALUES (?)
            ''', (self.name,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_users():
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return []

class Rental:
    def __init__(self, user_id, book_id, rental_date=None, return_date=None):
        self.user_id = user_id
        self.book_id = book_id
        self.rental_date = rental_date if rental_date else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.return_date = return_date

    def save_to_db(self):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO rentals (user_id, book_id, rental_date) 
                VALUES (?, ?, ?)
            ''', (self.user_id, self.book_id, self.rental_date))
            conn.commit()

    @classmethod
    def borrow_book(cls, user_id, book_id):
        try:
            # Creating new rental
            new_rental = cls(user_id, book_id)
            new_rental.save_to_db()

        # Update book availability
            Book.update_availability(book_id, decrement=True)
            return True
        except Exception as e:
            print(f"Failed to borrow book: {e}")
            return False

    @staticmethod
    def get_borrowed_books():
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                        SELECT r.id, b.title, u.name, r.return_date
                        FROM rentals r
                        JOIN books b ON r.book_id = b.id
                        JOIN users u ON r.user_id = u.id
                        WHERE r.return_date IS NULL
                    ''')
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def return_book(cls, rental_id):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT book_id FROM rentals WHERE id = ?', (rental_id,))
                book_id = cursor.fetchone()
                if book_id:
                    book_id = book_id[0]
                    # Update the rental with return date
                    return_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute('''
                        UPDATE rentals SET return_date =? WHERE id = ?
                    ''', (return_date, rental_id))
                    conn.commit()

                    # Update book availability
                    Book.update_availability(book_id, increment=True)
                    return True
                else:
                    print(f"No rental found with ID: {rental_id}")
                    return False
        except Exception as e:
            print(f"Failed to return book: {e}")
            return False


    @staticmethod
    def calculate_due_date(rental_date, rental_period=30):
        if isinstance(rental_date, str):
            rental_date = datetime.strptime(rental_date, '%Y-%m-%d %H:%M:%S')
        due_date = rental_date + timedelta(days=rental_period)
        return due_date.strftime('%Y-%m-%d %H:%M:%S')


    @staticmethod
    def get_all_rentals_with_details():
        # Fetch all rentals along with book title and user_name
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                        SELECT rentals.id AS rental_id, books.title, users.name, rentals.return_date
                        FROM rentals
                        JOIN books ON rentals.book_id = books.id
                        JOIN users ON rentals.user_id = users.id
                        ORDER BY rentals.return_date ASC  -- This orders by return date, but you can adjust as needed
            ''')
            return [dict(row) for row in cursor.fetchall()]
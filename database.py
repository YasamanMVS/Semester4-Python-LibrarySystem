import sqlite3

def create_connection(db_file):
    """ create a database connection to the SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.sqlite_version)
        return conn
    except sqlite3.Error as e:
        print(e)


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def main():
    database = "library_system.db"

    sql_create_books_table = """CREATE TABLE IF NOT EXISTS books (
                                 id integer PRIMARY KEY,
                                 title text NOT NULL,
                                 author text NOT NULL,
                                 category text NOT NULL,
                                 quantity integer NOT NULL DEFAULT 5,
                                 availability text NOT NULL DEFAULT 'yes'
                                 );"""

    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                            id integer PRIMARY KEY,
                                            name text NOT NULL
                                        ); """

    sql_create_rentals_table = """ CREATE TABLE IF NOT EXISTS rentals (
                                            id integer PRIMARY KEY,
                                            user_id integer NOT NULL,
                                            book_id integer NOT NULL,
                                            rental_date text NOT NULL,
                                            return_date text,
                                            FOREIGN KEY (user_id) REFERENCES users (id),
                                            FOREIGN KEY (book_id) REFERENCES books (id)
                                        ); """

    # Create a database connection
    conn = create_connection(database)

    # Create tables
    if conn is not None:
        # Create books table
        create_table(conn, sql_create_books_table)

        # Create users table
        create_table(conn, sql_create_users_table)

        # Create rentals table
        create_table(conn, sql_create_rentals_table)
    else:
        print("Error! cannot create the database connection.")

def insert_data():
    conn = sqlite3.connect('library_system.db')
    cur = conn.cursor()

    # Inserting data into the 'book' table
    books = [
        ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", "Fantasy", 10),
        ("Harry Potter and the Chamber of Secrets", "J.K. Rowling", "Fantasy", 10),
        ("Harry Potter and the Prisoner of Azkaban", "J.K. Rowling", "Fantasy", 10),
        ("Harry Potter and the Goblet of Fire", "J.K. Rowling", "Fantasy", 10),
        ("Harry Potter and the Order of the Phoenix", "J.K. Rowling", "Fantasy", 10),
        ("Harry Potter and the Half-Blood Prince", "J.K. Rowling", "Fantasy", 10),
        ("Harry Potter and the Deathly Hallows", "J.K. Rowling", "Fantasy", 10),
        ("The Handmaid's Tale", "Margaret Atwood", "Dystopian", 5),
        ("The Testaments", "Margaret Atwood", "Dystopian", 5),
        ("A Game of Thrones", "George R.R. Martin", "Fantasy", 10),
        ("A Clash of Kings", "George R.R. Martin", "Fantasy", 10),
        ("A Storm of Swords", "George R.R. Martin", "Fantasy", 10),
        ("A Feast for Crows", "George R.R. Martin", "Fantasy", 10),
        ("A Dance with Dragons", "George R.R. Martin", "Fantasy", 10),
    ]
    for book in books:
        title, author, category, quantity = book
        # Check if the book already exists
        cur.execute("SELECT id FROM books WHERE title = ? AND author = ?", (title, author))
        result = cur.fetchone()
        if result is None:
            # Book doesn't exist, insert it
            cur.execute('INSERT INTO books (title, author, category, quantity, availability) VALUES (?, ?, ?, ?, ?)',
                        (title, author, category, quantity, 'yes' if quantity > 0 else 'no'))


    # Insert data into the 'user' table
    users = [
        ('Yasaman Mirvahabi',),
        ('User Number2',),
        ('User Number3',),
        ('User Number4',),
        ('User Number5',),
        ('User Number6',),
        ('User Number7',),
        ('User Number8',)
    ]
    for user in users:
        name = user[0]
        # Check if the user already exists
        cur.execute("SELECT id FROM users WHERE name = ?", (name,))
        if cur.fetchone() is None:
            # User doesn't exist, insert it
            cur.execute('INSERT INTO users (name) VALUES (?)', (name,))

    # Save the changes and closing the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
    #delete_all_data()
    insert_data()
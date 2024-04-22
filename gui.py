import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox

from models import Book, Rental, User, get_db_connection
from database import main as initialize_database
initialize_database()


results_area = None

def setup_gui():
    # Main window
    root = tk.Tk()
    root.title("Library Management System")
    root.geometry("630x740")
    root.minsize(630, 740)

    # Style
    style = ttk.Style()
    style.theme_use('winnative')
    style.configure('TNotebook.Tab', font=('Buxton Sketch', '10', 'bold'))
    style.configure('TNotebook.Tab', padding=[15, 10])

    # Create Tab Control
    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # Tab 1: Books
    tab_all_books = ttk.Frame(tab_control)
    tab_control.add(tab_all_books, text='Books List')
    setup_all_books_tab(tab_all_books)

    # Tab 2: Users
    tab_all_users = ttk.Frame(tab_control)
    tab_control.add(tab_all_users, text='Users List')
    setup_all_users_tab(tab_all_users)

    # Tab 3: Search
    tab_search = ttk.Frame(tab_control)
    tab_control.add(tab_search, text='Search Books')
    setup_search_tab(tab_search)

    # Tab 4: Borrow
    tab_borrow = ttk.Frame(tab_control)
    tab_control.add(tab_borrow, text='Borrow Book')
    setup_borrow_tab(tab_borrow)

    # Tab 5: Return
    tab_return = ttk.Frame(tab_control)
    tab_control.add(tab_return, text='Return Book')
    setup_return_tab(tab_return)

    # Tab 6: Receipt
    tab_receipt = ttk.Frame(tab_control)
    tab_control.add(tab_receipt, text='Receipt')
    setup_receipt_tab(tab_receipt)

    tab_control.pack(expand=1, fill="both")
    root.mainloop()


#Function to set up books tab
def setup_all_books_tab(tab):
    scrollbar = tk.Scrollbar(tab)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    refresh_button = ttk.Button(tab, text="Refresh", command=display_all_books)
    refresh_button.pack(side=tk.TOP, pady=10)

    global books_result_area
    books_result_area = tk.Text(tab, yscrollcommand=scrollbar.set)
    books_result_area.pack(expand=True, fill='both')
    scrollbar.config(command=books_result_area.yview)

    display_all_books()

def display_all_books():
    books = Book.get_all_books()
    books_result_area.delete(1.0, tk.END)
    for index, book in enumerate(books, start=1):
        book_info = (
            f"{index}.\n"
            f"Title: {book['title']}\n"
            f"Author: {book['author']}\n"
            f"Category: {book['category']}\n"
            f"Availability: {book['availability']}\n"
            f"Quantity: {book['quantity']}\n\n"
        )
        books_result_area.insert(tk.END, book_info)


# Function to set up Users tab
def setup_all_users_tab(tab):
    scrollbar = tk.Scrollbar(tab)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    refresh_button = ttk.Button(tab, text="Refresh", command=display_all_users)
    refresh_button.pack(side=tk.TOP, pady=10)

    global users_result_area
    users_result_area = tk.Text(tab, yscrollcommand=scrollbar.set)
    users_result_area.pack(expand=True, fill='both')
    scrollbar.config(command=users_result_area.yview)

    display_all_users()

def display_all_users():
    users = User.get_all_users()
    users_result_area.delete(1.0, tk.END)
    for index, user in enumerate(users, start=1):
        name = user['name']
        user_info = f"{index}.\nName: {name}\n\n"
        users_result_area.insert(tk.END, user_info)


def setup_search_tab(tab):
    bold_font = ('Buxton Sketch', 10, 'bold')

    # Search query (title, author, or category)
    ttk.Label(tab, text="Enter Title, Author, or Category:", font=bold_font).grid(row=0, column=0, padx=10, pady=10)
    search_entry = ttk.Entry(tab)
    search_entry.grid(column=1, row=0, padx=10, pady=10)

    # Results area
    global results_area
    results_area = tk.Text(tab, height=10, width=50)
    results_area.grid(column=0, row=1, columnspan=3, padx=10, pady=10)

    # Search button
    search_button = ttk.Button(tab, text="Search", command=lambda: search_books(search_entry.get()))
    search_button.grid(column=2, row=0, padx=10, pady=10)

def search_books(search_entry):
    if results_area is not None:
        books = Book.search(search_entry)
        # Clear the results area
        results_area.delete('1.0', tk.END)
        if not books:
            results_area.insert(tk.END, "No books found.\n")
            return
        for index, book in enumerate(books, start=1):
            availability = 'Yes' if book['availability'] == 'yes' else 'No'
            book_info = (
                f"{index}.\n"
                f"Title: {book['title']}\n"
                f"Author: {book['author']}\n"
                f"Category: {book['category']}\n"
                f"Availability: {availability}\n"
                f"Quantity: {book['quantity']}\n\n"
            )
            results_area.insert(tk.END, book_info)

available_books_display = None
returned_books_display = None
book_id_entry = None
book_ids_for_borrowing = None

def setup_borrow_tab(tab):
    bold_font = ('Buxton Sketch', '10', 'bold')
    global book_id_entry, user_id_entry, book_ids_for_borrowing

    # Frame for the Refresh button
    refresh_frame = tk.Frame(tab)
    refresh_frame.pack(side=tk.TOP, fill='x')
    refresh_button = ttk.Button(refresh_frame, text="Refresh", command=refresh_books_and_users_display)
    refresh_button.pack(side=tk.TOP, pady=10)

    global available_books_display
    available_books_display = tk.Text(tab)
    available_books_display.pack(expand=True, fill='both')
    refresh_books_and_users_display()

    # Frame for the User ID and Entry
    user_frame = tk.Frame(tab)
    user_frame.pack(side=tk.TOP, fill='x', padx=10, pady=5)
    user_id_label = ttk.Label(user_frame, text="User ID: ", font=bold_font)
    user_id_label.pack(side=tk.LEFT)
    user_id_entry = ttk.Entry(user_frame)
    user_id_entry.pack(side=tk.LEFT)

    # Frame for the Book ID and Entry
    book_frame = tk.Frame(tab)
    book_frame.pack(side=tk.TOP, fill='x', padx=10, pady=5)
    book_id_label = ttk.Label(book_frame, text="Book ID:", font=bold_font)
    book_id_label.pack(side=tk.LEFT)
    book_id_entry = ttk.Entry(book_frame)
    book_id_entry.pack(side=tk.LEFT, padx=(0, 10))

    # Add Button to add selected book ID to the Listbox
    add_book_button = ttk.Button(book_frame, text="Add", command=add_book_to_list)
    add_book_button.pack(side=tk.LEFT, padx=10)

    # Frame for the "Books for Borrow" Label and Listbox
    books_to_borrow_frame = tk.Frame(tab)
    books_to_borrow_frame.pack(side=tk.TOP, fill='x', padx=10, pady=5)
    books_to_borrow_label = ttk.Label(books_to_borrow_frame, text="Books to Borrow:", font=bold_font)
    books_to_borrow_label.pack(side=tk.TOP, padx=10, anchor="w")

    # Initializing the Listbox for selected book IDs
    book_ids_for_borrowing = tk.Listbox(books_to_borrow_frame, height=5, width=20)
    book_ids_for_borrowing.pack(side=tk.TOP, fill='x', padx=10, pady=5)

    # Frame for the Borrow Book button
    borrow_button_frame = tk.Frame(tab)
    borrow_button_frame.pack(side=tk.TOP, padx=10, pady=10)
    borrow_button = ttk.Button(borrow_button_frame, text="Borrow", command=borrow_books)
    borrow_button.pack(side=tk.TOP, pady=10)

def add_book_to_list():
    book_id = book_id_entry.get().strip()
    if book_id:
        book_ids_for_borrowing.insert(tk.END, book_id)
        book_id_entry.delete(0, tk.END)  # Clear the entry field after adding
    else:
        messagebox.showwarning("Warning", "Please enter a Book ID to add.")

def refresh_books_and_users_display():
    available_books = Book.get_all_books()
    all_users = User.get_all_users()

    available_books_display.delete('1.0', tk.END)
    available_books_display.insert(tk.END, "List of Available Books:\n")
    for index, book in enumerate(available_books, 1):
        if book['availability'] == 'yes':
            book_info = f"{index}.\nTitle: {book['title']}\nAuthor: {book['author']}\nQuantity: {book['quantity']}\n\n"
            available_books_display.insert(tk.END, book_info)

    available_books_display.insert(tk.END, "\nList of Users:\n")
    for index, user in enumerate(all_users, 1):
        user_info = f"{index}.\nName: {user['name']}\n\n"
        available_books_display.insert(tk.END, user_info)


def borrow_books():
    global user_id_entry
    user_id = user_id_entry.get()
    if not user_id:
        messagebox.showerror("Error", "Please enter a User ID.")
        return


    user_name = fetch_user_name(user_id)
    if user_name is None:
        messagebox.showerror("Error", "Invalid User ID.")
        return

    success = True
    books_borrowed_ids = []
    for book_id in book_ids_for_borrowing.get(0, tk.END):
        if not Rental.borrow_book(user_id, book_id):
            success = False
            messagebox.showerror("Error", f"Failed to borrow book ID {book_id}.")
            break
        else:
            books_borrowed_ids.append(book_id)

    if success:
        messagebox.showinfo("Success", "All selected books have been borrowed successfully.\n")
        messagebox.showinfo("Receipt", "Check your receipt in Receipt tab")
        # Generate the receipt
        generate_receipt(books_borrowed_ids, user_id)
        book_ids_for_borrowing.delete(0, tk.END)  # Clear the list after borrowing
    refresh_books_and_users_display()

def fetch_user_name(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        if user_row:
            return user_row['name']
        else:
            return None

def fetch_borrowed_book_info(book_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
                    SELECT b.title, b.author, r.rental_date, r.return_date
                    FROM books b
                    JOIN rentals r ON b.id = r.book_id
                    WHERE b.id = ? AND r.return_date IS NULL
                ''', (book_id,))
        book_row = cursor.fetchone()
        if book_row:
            return {
                'title': book_row['title'],
                'author': book_row['author'],
                'rental_date': book_row['rental_date'],
                'due_date': (datetime.strptime(book_row['rental_date'], '%Y-%m-%d %H:%M:%S') + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return None

def setup_return_tab(tab):
    bold_font = ('Buxton Sketch', 10, 'bold')

    refresh_return_button = ttk.Button(tab, text="Refresh", command=refresh_return_books_display)
    refresh_return_button.pack(side=tk.TOP, padx=10, pady=5)

    global returned_books_display
    returned_books_display = tk.Text(tab)
    returned_books_display.pack(expand=True, fill='both')
    refresh_return_books_display()

    rental_id_label = ttk.Label(tab, text="Rental ID:", font=bold_font)
    rental_id_label.pack(side=tk.TOP, padx=10, pady=5)

    rental_id_entry = ttk.Entry(tab)
    rental_id_entry.pack(side=tk.TOP, padx=10, pady=5)

    return_button = ttk.Button(tab, text="Return", command=lambda: return_book(rental_id_entry.get()))
    return_button.pack(side=tk.TOP, padx=10, pady=5)



def refresh_return_books_display():
    all_rentals = Rental.get_all_rentals_with_details()
    returned_books_display.delete('1.0', tk.END)
    for rental in all_rentals:
        return_status = "Returned" if rental['return_date'] else "Not Returned"
        display_info = (
            f"Rental ID: {rental['rental_id']}\n"
            f"Title: {rental['title']}\n"
            f"Borrowed by: {rental['name']}\n"
            f"Status: {return_status}\n\n"
        )
        returned_books_display.insert(tk.END, display_info)

def return_book(rental_id):
    success = Rental.return_book(rental_id=rental_id)
    if success:
        messagebox.showinfo("Success", "Book returned successfully!")
        refresh_return_books_display()
    else:
        messagebox.showerror("Error", "Failed to return book.")


def setup_receipt_tab(tab):
    global receipt_display

    receipt_frame = tk.Frame(tab)
    receipt_frame.pack(side=tk.TOP, fill='both', expand=True)

    # Create and pack the receipt text area
    receipt_display = tk.Text(receipt_frame, height=20, width=50)
    receipt_display.pack(side=tk.LEFT, fill='both', expand=True)

    # Scrollbar for the text area
    receipt_scrollbar = ttk.Scrollbar(receipt_frame, command=receipt_display.yview)
    receipt_scrollbar.pack(side=tk.RIGHT, fill='y')
    receipt_display['yscrollcommand'] = receipt_scrollbar.set

def update_receipt(receipt_info):
    # Clear the receipt display
    receipt_display.delete('1.0', tk.END)

    # Header
    receipt_display.insert(tk.END, 'Library Receipt\n\n')

    # Details
    for book in receipt_info['books']:
        receipt_display.insert(tk.END, f"Title: {book['title']}\n")
        receipt_display.insert(tk.END, f"Borrowed by: {receipt_info['name']}\n")
        receipt_display.insert(tk.END, f"User ID: {receipt_info['id']}\n")
        receipt_display.insert(tk.END, f"Borrowed on: {book['rental_date']}\n")
        receipt_display.insert(tk.END, f"Must be returned by: {book['due_date']}\n\n")

    receipt_display.config(state=tk.DISABLED)
    
def generate_receipt(books_borrowed_ids, user_id):
    user_name = fetch_user_name(user_id)
    receipt_books_info = []

    for book_id in books_borrowed_ids:
        book_info = fetch_borrowed_book_info(book_id)
        if book_info:
            receipt_books_info.append(book_info)

    receipt_info = {
        'books': receipt_books_info,
        'name': user_name,
        'id': user_id
    }

    update_receipt(receipt_info)

# RUN IT

if __name__ == '__main__':
    setup_gui()
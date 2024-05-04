# Library System

## Project Overview:
This project implements a library management system in Python using SQLite for the backend. The system allows for managing books, users, and rentals through a graphical user interface (GUI) built with Tkinter. Features include adding books and users, borrowing and returning books, and viewing all books and users in the system.

## Features:
- **Book Management**: Add and manage books with details such as title, author, and quantity.
- **User Management**: Add and manage library users.
- **Rental Management**: Users can borrow and return books. The system tracks all rentals.
- **Search Functionality**: Search for books by title, author, or category.
- **GUI**: A user-friendly graphical interface for interacting with the library system.

## Installation:
Ensure Python 3 is installed on your system. Clone the repository and install dependencies:
```bash
git clone https://github.com/YasamanMVS/Semester4-Python-LibrarySystem.git
cd LibrarySystem
```
## Usage:
To run the library system, execute the following command:
```bash
python app.py
```
Follow the GUI prompts to interact with the system.

## Project Structure:
- **app.py**: The main Python script that launches the GUI for the library system.
- **database.py**: Contains all database connection and schema setup functions.
- **gui.py**: Manages all GUI components and interactions.
- **models.py**: Defines data models and database interaction methods for books, users, and rentals.

## Database Schema:
- **Books**: `id`, `title`, `author`, `category`, `quantity`, `availability`
- **Users**: `id`, `name`
- **Rentals**: `id`, `user_id`, `book_id`, `rental_date`, `return_date`

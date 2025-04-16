from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime, timedelta
from bson import ObjectId
import pymongo

# Initialize Faker
fake = Faker()

# Constants
GENRES = [
    'Fiction', 'Non-Fiction', 'Science Fiction', 'Fantasy', 'Mystery',
    'Thriller', 'Romance', 'Horror', 'Biography', 'History',
    'Science', 'Poetry', 'Children', 'Young Adult', 'Cookbook',
    'Travel', 'Self-Help', 'Religion', 'Art', 'Technology'
]
DATABASE_NAME = "mybookstore"

# MongoDB setup
def get_database_connection():
    client = MongoClient("mongodb://localhost:27017/")
    return client[DATABASE_NAME]

# Generate authors
def generate_authors(num_authors=50):
    return [{
        'name': fake.name(),
        'bio': fake.text(max_nb_chars=200),
        'created_at': datetime.now()
    } for _ in range(num_authors)]

# Generate customers
def generate_customers(num_customers=100):
    return [{
        'name': fake.name(),
        'email': fake.email(),
        'address': fake.address(),
        'phone': fake.phone_number(),
        'created_at': datetime.now()
    } for _ in range(num_customers)]

# Generate books with references to authors
def generate_books(authors, num_books=200):
    return [{
        'title': fake.catch_phrase(),
        'author_id': random.choice(authors)['_id'],
        'isbn': fake.isbn13(),
        'genre': random.choice(GENRES),
        'price': round(random.uniform(5.99, 29.99), 2),
        'pages': random.randint(100, 800),
        'published_date': datetime.combine(fake.date_between(start_date='-20y', end_date='today'), datetime.min.time()),
        'in_stock': random.randint(0, 100),
        'rating': round(random.uniform(1, 5), 1),
        'created_at': datetime.now()
    } for _ in range(num_books)]

# Generate orders with references to books and customers
def generate_orders(customers, books, num_orders=300):
    orders = []
    for _ in range(num_orders):
        customer = random.choice(customers)
        book = random.choice(books)
        quantity = random.randint(1, 5)
        total_amount = round(quantity * book['price'], 2)
        order_date = datetime.combine(fake.date_between(start_date='-2y', end_date='today'), datetime.min.time())
        orders.append({
            'customer_id': customer['_id'],
            'book_id': book['_id'],
            'quantity': quantity,
            'total_amount': total_amount,
            'order_date': order_date,
            'created_at': datetime.now()
        })
    return orders

# Insert data into MongoDB
def insert_data():
    db = get_database_connection()

    author_collection = db["authors"]
    customer_collection = db["customers"]
    book_collection = db["books"]
    order_collection = db["orders"]

    try:
        # Insert Authors
        authors_data = generate_authors()
        author_result = author_collection.insert_many(authors_data)
        for i, _id in enumerate(author_result.inserted_ids):
            authors_data[i]['_id'] = _id
        print(f"Inserted {len(author_result.inserted_ids)} authors.")

        # Insert Customers
        customers_data = generate_customers()
        customer_result = customer_collection.insert_many(customers_data)
        for i, _id in enumerate(customer_result.inserted_ids):
            customers_data[i]['_id'] = _id
        print(f"Inserted {len(customer_result.inserted_ids)} customers.")

        # Insert Books
        books_data = generate_books(authors_data)
        book_result = book_collection.insert_many(books_data)
        for i, _id in enumerate(book_result.inserted_ids):
            books_data[i]['_id'] = _id
        print(f"Inserted {len(book_result.inserted_ids)} books.")

        # Insert Orders
        orders_data = generate_orders(customers_data, books_data)
        order_result = order_collection.insert_many(orders_data)
        print(f"Inserted {len(order_result.inserted_ids)} orders.")

    except pymongo.errors.PyMongoError as e:
        print(f"MongoDB error: {e}")

# Main runner
if __name__ == "__main__":
    insert_data()

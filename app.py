import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import uuid
from datetime import datetime
from model.models import SweetShop

from flask import Flask, render_template, request, redirect, url_for, session, flash
# from bson import ObjectId

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB connection string from environment variable
MONGODB_URI = os.getenv("DB_CONNECTION_STRING")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in .env file")

# Connect to MongoDB Atlas
client = MongoClient(MONGODB_URI)

# Example: Access a database and collection
db = client[os.getenv("DB_NAME")]  # Replace with your database name
Account_Collection = db[os.getenv("DB_ACCOUNT_COLLECTION")]  # Replace with your collection name

try:
    shop = SweetShop(connection_string=MONGODB_URI, db_name=os.getenv("DB_NAME"))
except pymongo.errors.ConnectionError as e:
    print(f"Could not connect to MongoDB: {e}")
    raise
# # Test the connection
# print("Collections:", db.list_collection_names())

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY_FLASK")


# --- Main Routes ---

@app.route('/')
def index():
    """Displays the main page with a list of all sweets."""
    all_sweets = shop.get_all_sweets()
    return render_template('index.html', sweets=all_sweets)

@app.route('/search')
def search():
    """Handles searching for sweets based on query parameters."""
    query = request.args.get('query', '')
    search_by = request.args.get('by', 'name')
    results = []

    if query:
        if search_by == 'name':
            results = shop.search_by_name(query)
        elif search_by == 'category':
            results = shop.search_by_category(query)
    
    return render_template('search.html', results=results, query=query, search_by=search_by)

# --- User Authentication Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('register'))
        try:
            # In a real app, you would hash the password here before storing it.
            shop.register_user(username, password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # This is a simple login check. A real app would verify a hashed password.
        user = shop.users_collection.find_one({"username": username, "password": password})
        if user:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/history')
def history():
    """Displays the purchase history for the logged-in user."""
    if 'username' not in session:
        flash('You must be logged in to view your purchase history.', 'warning')
        return redirect(url_for('login'))
    
    purchase_history = shop.get_purchase_history(session['username'])
    return render_template('history.html', history=purchase_history)

# --- Inventory Management Routes ---

@app.route('/add_sweet', methods=['GET', 'POST'])
def add_sweet():
    """Page for adding a new sweet to the inventory."""
    if 'username' not in session: # A simple authorization check
        flash('You must be logged in to add a sweet.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            name = request.form['name']
            category = request.form['category']
            price = float(request.form['price'])
            quantity = int(request.form['quantity'])
            shop.add_sweet(name, category, price, quantity)
            flash(f"Sweet '{name}' was added successfully!", 'success')
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e), 'danger') # Handles duplicate ID or bad number format
        except Exception as e:
            flash(f"An unexpected error occurred: {e}", 'danger')
    
    return render_template('add_sweet.html')

@app.route('/purchase/<int:sweet_id>', methods=['POST'])
def purchase_sweet_route(sweet_id):
    """Handles the purchasing of a sweet."""
    if 'username' not in session:
        flash('You must be logged in to make a purchase.', 'warning')
        return redirect(url_for('login'))

    try:
        quantity = int(request.form.get('quantity', 1))
        shop.purchase_sweet(session['username'], sweet_id, quantity)
        flash('Your purchase was successful!', 'success')
    except (KeyError, ValueError) as e:
        flash(f"Purchase failed: {e}", 'danger') # Catches invalid ID or insufficient stock
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # The debug=True flag enables auto-reloading and provides helpful error pages.
    # Do not use debug=True in a production environment.
    app.run(debug=True)
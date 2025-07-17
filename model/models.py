import pymongo
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
import uuid

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


class SweetShop:
    def __init__(self, connection_string, db_name):
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            self.sweets_collection = self.db['sweets']
            self.users_collection = self.db['users']
            
            # Ensure unique indexes for data integrity
            self.sweets_collection.create_index([('sweet_id', pymongo.ASCENDING)], unique=True)
            self.users_collection.create_index([('username', pymongo.ASCENDING)], unique=True)

        except pymongo.errors.ConnectionError as e:
            print(f"Could not connect to MongoDB: {e}")
            raise
        self.sweets = []

    def register_user(self, username, password):

        user_document = {
            "username": username,
            "password": password, # In a real app, HASH THIS PASSWORD!
            "role": "customer",
            "purchaseHistory": [],
            "createdAt": datetime.now(),
            # "updatedAt": datetime.utcnow()
        }
        try:
            self.users_collection.insert_one(user_document)
            print(f"User {username} added successfully.")
        except pymongo.errors.DuplicateKeyError:
            print(f"User {username} already exists.")

    def get_purchase_history(self, username):
        user = self.users_collection.find_one({"username": username})
        if user:
            return user.get("purchaseHistory", [])

    def add_sweet(self, name, category, price, quantity):

        sweet_document = {
            "sweet_id": str(uuid.uuid4()),
            "name": name,
            "category": category,
            "price": price,
            "quantity": quantity,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        try:
            result = self.sweets_collection.insert_one(sweet_document)
            return result.inserted_id
        except pymongo.errors.DuplicateKeyError:
            raise ValueError(f"A sweet with ID {sweet_document['sweet_id']} already exists.")

    def delete_sweet(self, sweet_id):
        result = self.sweets_collection.delete_one({"sweet_id": sweet_id})
        if result.deleted_count == 0:
            raise ValueError(f"No sweet found with ID {sweet_id}.")
        return True

    def get_all_sweets(self):
        return list(self.sweets_collection.find())
    
    def search_by_name(self, name):
        """Searches for sweets by name (case-insensitive)."""
        return list(self.sweets_collection.find({"name": {"$regex": name, "$options": "i"}}))
    
    def search_by_category(self, category):
        """Searches for sweets by category (case-insensitive)."""
        return list(self.sweets_collection.find({"category": {"$regex": category, "$options": "i"}}))

    def search_by_price_range(self, min_price, max_price):
        """Searches for sweets within a price range."""
        return list(self.sweets_collection.find({"price": {"$gte": min_price, "$lte": max_price}}))
    
    def sort_by(self, key):
        """Sorts the sweets collection by a given key."""
        return list(self.sweets_collection.find({}, {'_id': 0}).sort(key, pymongo.ASCENDING))
    
    def purchase_sweet(self, username, sweet_id, quantity):
        """Purchases a sweet and updates the user's purchase history."""
        sweet = self.sweets_collection.find_one({"sweet_id": sweet_id})
        user = self.users_collection.find_one({"username": username})

        if not user:
            raise KeyError(f"No user found with username '{username}'.")
        if not sweet:
            raise KeyError(f"No sweet found with ID {sweet_id}.")
        
        if sweet['quantity'] < quantity:
            raise ValueError(f"Insufficient stock for '{sweet['name']}'. "
                             f"Available: {sweet['quantity']}, Requested: {quantity}")
        
        self.sweets_collection.update_one(
            {"sweet_id": sweet_id},
            {"$inc": {"quantity": -quantity}, "$set": {"updatedAt": datetime.now()}}
        )

        purchase_record = {
            "orderId": str(uuid.uuid4()),
            "sweet_id": sweet_id,
            "name": sweet['name'],
            "quantity": quantity,
            "pricePerUnit": sweet['price'],
            "totalAmount": sweet['price'] * quantity,
            "purchaseDate": datetime.utcnow()
        }
        self.users_collection.update_one(
            {"username": username},
            {"$push": {"purchaseHistory": purchase_record}}
        )
        return purchase_record['orderId']
    
    def restock_sweet(self, sweet_id, quantity_to_add):
        """Increases the stock of a sweet."""
        result = self.sweets_collection.update_one(
            {"sweet_id": sweet_id},
            {"$inc": {"quantity": quantity_to_add}, "$set": {"updatedAt": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise KeyError(f"No sweet found with ID {sweet_id} to restock.")
        
    def close_connection(self):
        """Closes the connection to the MongoDB server."""
        self.client.close()
        print("MongoDB connection closed.")




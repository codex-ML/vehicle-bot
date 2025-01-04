import os
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)

db = client['telegram_bot']

users_collection = db['users']


def user_exists(user_id):
    return users_collection.find_one({"user_id": user_id}) is not None


def add_user(user_id, username):
    user = {"user_id": user_id, "username": username}
    users_collection.insert_one(user)


def get_all_users():
    """Fetch all users from the database."""
    return users_collection.find()
    
def get_user_count():
    try:
        return users_collection.count_documents({})
    except Exception as e:
        print(f"Error: {e}")
        return 0

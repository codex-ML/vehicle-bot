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

def check_rate_limit(user_id):
    """
    Check if user has remaining queries within the rate limit.
    Returns tuple (bool, int) - (can_proceed, remaining_queries)
    """
    current_time = datetime.utcnow()
    one_hour_ago = current_time - timedelta(hours=1)
    
    # Find or create rate limit document for user
    rate_limit = rate_limits_collection.find_one({"user_id": user_id})
    
    if not rate_limit:
        # Create new rate limit entry
        rate_limit = {
            "user_id": user_id,
            "queries_remaining": 3,
            "reset_time": current_time + timedelta(hours=1)
        }
        rate_limits_collection.insert_one(rate_limit)
        return True, 3
    
    # Check if we need to reset the limit
    if rate_limit["reset_time"] < current_time:
        rate_limits_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "queries_remaining": 3,
                    "reset_time": current_time + timedelta(hours=1)
                }
            }
        )
        return True, 3
    
    # Check if user has remaining queries
    remaining = rate_limit["queries_remaining"]
    can_proceed = remaining > 0
    
    return can_proceed, remaining

def decrement_queries(user_id):
    """
    Decrement the remaining queries for a user.
    Returns the number of queries remaining.
    """
    rate_limits_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"queries_remaining": -1}}
    )
    
    rate_limit = rate_limits_collection.find_one({"user_id": user_id})
    return rate_limit["queries_remaining"]

def get_reset_time(user_id):
    """
    Get the time when the user's rate limit will reset.
    """
    rate_limit = rate_limits_collection.find_one({"user_id": user_id})
    if rate_limit:
        return rate_limit["reset_time"]
    return None

import os
from datetime import datetime
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
load_dotenv()
MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME')

MongoURL = os.environ.get('MONGO')
MongoDB_Name = 'test'
def connect_to_db():
    client = MongoClient(MongoURL)
    # client = MongoClient(MongoURL)
    db = client[MongoDB_Name]
    users = db["users"]
    message_history = db["message_history"]
    llm_message_history = db["llm_message_history"]
    user_preferences = db["user_preferences"]
    return users, message_history, user_preferences, llm_message_history

def connect_to_db_free():
    client = MongoClient(MongoURL)
    # client = MongoClient(MongoURL)
    db = client[MongoDB_Name]
    user_free_trail = db["free_trial"]
    return user_free_trail

def connect_to_db_extras():
    client = MongoClient(MongoURL)
    # client = MongoClient(MongoURL)
    db = client[MongoDB_Name]
    user_extras = db["extras"]
    return user_extras
    
def create_or_update_user_extra(user_id):
    users = connect_to_db_extras()
    current_time = datetime.now()
    # The upsert=True option creates a new document if no document matches the filter
    users.update_one(
        {'user_id': user_id},
        {'$set': {'last_message_time': current_time}},
        upsert=True
    )

def get_user_extras():
    users = connect_to_db_extras()
    all_users = list(users.find())
    return all_users
    # found = users.find_one({'user_id': user_id})
    # if found:
    #     return True, found
    # else:
    #     return False , None

def create_user_free(user_id):
    users= connect_to_db_free()
    users.insert_one({'user_id': user_id, "left": 2})

def get_user_free(user_id):
    users = connect_to_db_free()
    found = users.find_one({'user_id': user_id})
    if found:
        return True, found
    else:
        return False , None

def update_user_free(user_id, left_messages):
    users = connect_to_db_free()
    users.update_one({'user_id': user_id}, {'$set': {'left': left_messages}})

def change_preferences(user_id, user_pref):
    _, _ , user_preferences,_ = connect_to_db()
    user_preferences.update_one({'user_id': user_id}, {'$set': {'local_llm': user_pref}})
def save_preferences_to_db(user_id, user_name ,user_pref):
    _, _ , user_preferences, _ = connect_to_db()
    user_preferences.insert_one({'user_id': user_id, 'user_name': user_name, 'local_llm': user_pref, 'voice': False})
def change_voice(user_id, user_pref):
    _, _ , user_preferences,_ = connect_to_db()
    user_preferences.update_one({'user_id': user_id}, {'$set': {'voice': user_pref}}) 
def get_preferences(user_id):
    _, _, user_preferences, _ = connect_to_db()
    found = user_preferences.find_one({'user_id': user_id})
    if found:
        return True, found
    else:
        return False , None
def save_message_to_db(user_id, user_text, model_res):
    users, message_history, _, _ = connect_to_db()
    new_messages = [{'user': user_text}, {'bot': model_res}]
    # Append messages to an existing conversation or create a new conversation
    message_history.update_one(
        {'user_id': user_id},
        {'$push': {'messages': {'$each': new_messages}}},
        upsert=True)

def delete_message_history(user_id):
    users, message_history, _, _ = connect_to_db()
    message_history.delete_many({'user_id': user_id})

def create_user(user_id, user_name):
    users, _ , _, _= connect_to_db()
    users.insert_one({'user_id': user_id, 'user_name': user_name, 'last_message_time': 0, 'payment_status': False})

def all_users():
    users, _ , _, _= connect_to_db()
    return users.find({})

def get_user(user_id):
    users, _, _, _ = connect_to_db()
    found = users.find_one({'user_id': user_id})
    if found:
        return True, found
    else:
        return False , None
def update_user(user_id):
    users, _ , _, _= connect_to_db()
    users.update_one({'user_id': user_id}, {'$set': {'payment_status': False}})

def update_user_time(user_id, time_left):
    users, _, _, _ = connect_to_db()
    users.update_one({'user_id': user_id}, {'$set': {'last_message_time': time_left}})


def save_message_llm_to_db(user_id, user_text, model_res):
    _, _, _, message_history = connect_to_db()
    new_messages = [{'user': user_text}, {'bot': model_res}]
    
    # Append messages to an existing conversation or create a new conversation
    message_history.update_one(
        {'user_id': user_id},
        {'$push': {'messages': {'$each': new_messages}}},
        upsert=True
    )

def delete_message_llm_history(user_id):
    _, _, _, message_history = connect_to_db()
    message_history.delete_many({'user_id': user_id})

if __name__ == '__main__':
    _, _, _, _ = connect_to_db()

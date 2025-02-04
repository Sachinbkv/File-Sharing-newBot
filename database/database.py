#(©)CodeXBotz




import pymongo, os
from config import DB_URI, DB_NAME
from datetime import datetime


async def update_last_api_call(user_id: int, last_api_call: datetime):
    user_data.update_one({'_id': user_id}, {'$set': {'last_api_call': last_api_call}})
    return


dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]


user_data = database['users']



async def present_user(user_id : int):
    found = user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    for doc in user_docs:
        user_ids.append(doc['_id'])
        
    return user_ids

async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    return

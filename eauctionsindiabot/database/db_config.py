import pymongo
from pymongo.errors import PyMongoError
from custom_exceptions.exceptions import DatabaseError
import os
import dotenv
dotenv.load_dotenv()


def get_eauctionindiadb_connection():
    database_url = os.getenv('DATABASE_URL')
    try:
        conn  = pymongo.MongoClient(database_url)
        db = conn['Zbot']
        coll = db['Eauctionindia']
        return coll
    except PyMongoError as e:
        raise DatabaseError(f"Database connection failed: {e}")

def get_script_log_connection():
    database_url = os.getenv('DATABASE_URL')
    try:
        conn = pymongo.MongoClient(database_url)
        db = conn['Zbot']
        coll = db['Script_logs']
        return coll
    except PyMongoError as e:
        raise DatabaseError(f"Database connection failed: {e}")

    


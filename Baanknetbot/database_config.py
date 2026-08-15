from pymongo import MongoClient,errors
import os
import dotenv
import asyncpg
dotenv.load_dotenv()

def get_baanknet_collection():
    database_url = os.getenv('DATABASE_URL')
    try:
        conn  = MongoClient(database_url)
        db = conn['Zbot']
        coll = db['baanknet']
        return coll
    except errors.PyMongoError as e:
        raise Exception(f"Database connection failed unable to fetch the collection: {e}")

async def get_postgresql_database_connection()->asyncpg.connection.Connection:
    database_url = os.getenv('PG_DATABASE_URL')
    try:
        connection : asyncpg.connection.Connection = await asyncpg.connect(database_url)
        return connection
    except asyncpg.PostgresConnectionError as e:
        print(f"PostgreSQL connection failed: {e}")
        raise e

    except Exception as e:
        print(f"Unexpected database error: {e}")
        raise e
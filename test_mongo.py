# test_mongo.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)

try:
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    
    # List databases
    print("📊 Available databases:", client.list_database_names())
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
finally:
    client.close()
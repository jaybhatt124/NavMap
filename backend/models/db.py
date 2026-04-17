from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

_db = None

def get_db():
    global _db
    if _db is None:
        uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/navmap')
        print(f">>> Connecting to MongoDB: {uri[:40]}...")
        client = MongoClient(uri, serverSelectionTimeoutMS=10000)
        _db = client[os.getenv('DB_NAME', 'navmap')]
        try:
            _db.users.create_index('email', unique=True)
            _db.organizations.create_index('name', unique=True)
            _db.scan_logs.create_index([('org_id', ASCENDING), ('scanned_at', ASCENDING)])
            print(">>> MongoDB connected & indexes created")
        except Exception as e:
            print(f">>> Index note: {e}")
    return _db

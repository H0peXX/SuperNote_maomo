from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

# Import mock database for fallback
try:
    from database.mock_db import init_mock_database, close_mock_database, get_mock_database
    MOCK_DB_AVAILABLE = True
except ImportError:
    MOCK_DB_AVAILABLE = False

load_dotenv()

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None
    using_mock = False

db = MongoDB()

async def init_database():
    """Initialize MongoDB connection with fallback to mock database"""
    try:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "maomo_db")
        
        db.client = AsyncIOMotorClient(mongodb_url)
        db.database = db.client[database_name]
        
        # Test the connection
        await db.client.admin.command('ping')
        logging.info(f"✅ Connected to MongoDB at {mongodb_url}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logging.warning(f"⚠️ MongoDB connection failed: {e}")
        if MOCK_DB_AVAILABLE:
            logging.info("🔄 Falling back to mock database for testing...")
            await init_mock_database()
            db.database = get_mock_database()
            db.using_mock = True
            await create_indexes()  # Create mock indexes
        else:
            logging.error("❌ Mock database not available. Please install MongoDB or check connection.")
            raise

async def close_database():
    """Close database connection"""
    if db.using_mock:
        await close_mock_database()
    elif db.client:
        db.client.close()
        logging.info("MongoDB connection closed")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("username", unique=True)
        
        # Teams collection indexes
        await db.database.teams.create_index("name")
        await db.database.teams.create_index("members.user_id")
        
        # Notes collection indexes
        await db.database.notes.create_index([("team_id", 1), ("topic", 1)])
        await db.database.notes.create_index("created_at")
        await db.database.notes.create_index("updated_at")
        
        # Topics collection indexes
        await db.database.topics.create_index([("team_id", 1), ("name", 1)], unique=True)
        
        logging.info("Database indexes created successfully")
        
    except Exception as e:
        logging.error(f"Error creating indexes: {e}")

def get_database():
    """Get database instance"""
    return db.database

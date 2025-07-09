#!/usr/bin/env python3
"""
Test script to verify the backend works with mock database
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_backend():
    """Test basic backend functionality"""
    try:
        # Test imports
        from database.mongodb import init_database, get_database
        from backend.models.schemas import UserCreate, TeamCreate, TopicCreate
        from dotenv import load_dotenv
        
        load_dotenv()
        
        print("✅ All imports successful")
        
        # Initialize database
        await init_database()
        db = get_database()
        
        print("✅ Database initialized successfully")
        
        # Test creating a user
        from datetime import datetime
        from backend.auth.jwt_handler import get_password_hash
        
        user_doc = {
            "username": "testuser",
            "email": "test@example.com", 
            "full_name": "Test User",
            "hashed_password": get_password_hash("testpassword"),
            "role": "member",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_doc)
        print(f"✅ Created test user with ID: {result.inserted_id}")
        
        # Test finding the user
        found_user = await db.users.find_one({"email": "test@example.com"})
        if found_user:
            print(f"✅ Found user: {found_user['full_name']}")
        else:
            print("❌ Could not find test user")
            
        print("\n🎉 Backend test completed successfully!")
        print("You can now:")
        print("1. Start the backend: python start_backend.py")
        print("2. Start the frontend: streamlit run frontend/app.py")
        print("3. Open http://localhost:8501 in your browser")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend())
    sys.exit(0 if success else 1)

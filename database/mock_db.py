"""
Mock database implementation for testing without MongoDB
This allows us to test the application structure without requiring MongoDB installation
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
try:
    from bson import ObjectId
except ImportError:
    # Fallback ObjectId implementation for testing
    import uuid
    class ObjectId:
        def __init__(self, oid=None):
            self._id = oid or str(uuid.uuid4()).replace('-', '')[:24]
        
        def __str__(self):
            return self._id
        
        def __eq__(self, other):
            return str(self) == str(other)
import asyncio

class MockCollection:
    """Mock MongoDB collection"""
    
    def __init__(self, name: str):
        self.name = name
        self.data: Dict[str, Dict] = {}
        self.indexes = set()
        self.database = None  # Will be set by database
    
    async def find_one(self, filter_dict: Dict = None, projection: Dict = None) -> Optional[Dict]:
        """Find one document"""
        if not filter_dict:
            filter_dict = {}
        
        for doc_id, doc in self.data.items():
            if self._matches_filter(doc, filter_dict):
                result = doc.copy()
                if projection:
                    # Apply projection (simplified)
                    if any(v == 0 for v in projection.values()):
                        # Exclusion projection
                        for field, include in projection.items():
                            if include == 0 and field in result:
                                del result[field]
                return result
        return None
    
    def find(self, filter_dict: Dict = None, projection: Dict = None):
        """Find multiple documents"""
        return MockCursor(self, filter_dict, projection)
    
    async def insert_one(self, document: Dict) -> 'MockInsertResult':
        """Insert one document"""
        doc_id = str(ObjectId())
        document["_id"] = ObjectId(doc_id)
        self.data[doc_id] = document.copy()
        if self.database:
            self.database.save_data()
        return MockInsertResult(doc_id)
    
    async def update_one(self, filter_dict: Dict, update: Dict) -> 'MockUpdateResult':
        """Update one document"""
        for doc_id, doc in self.data.items():
            if self._matches_filter(doc, filter_dict):
                if "$set" in update:
                    doc.update(update["$set"])
                if "$push" in update:
                    for field, value in update["$push"].items():
                        if field not in doc:
                            doc[field] = []
                        doc[field].append(value)
                if "$pull" in update:
                    for field, condition in update["$pull"].items():
                        if field in doc and isinstance(doc[field], list):
                            doc[field] = [item for item in doc[field] if not self._matches_filter(item, condition)]
                if self.database:
                    self.database.save_data()
                return MockUpdateResult(1)
        return MockUpdateResult(0)
    
    async def delete_one(self, filter_dict: Dict) -> 'MockDeleteResult':
        """Delete one document"""
        for doc_id, doc in list(self.data.items()):
            if self._matches_filter(doc, filter_dict):
                del self.data[doc_id]
                if self.database:
                    self.database.save_data()
                return MockDeleteResult(1)
        return MockDeleteResult(0)
    
    async def delete_many(self, filter_dict: Dict) -> 'MockDeleteResult':
        """Delete multiple documents"""
        deleted_count = 0
        for doc_id, doc in list(self.data.items()):
            if self._matches_filter(doc, filter_dict):
                del self.data[doc_id]
                deleted_count += 1
        if deleted_count > 0 and self.database:
            self.database.save_data()
        return MockDeleteResult(deleted_count)
    
    async def create_index(self, keys, **kwargs):
        """Create index (mock)"""
        if isinstance(keys, str):
            self.indexes.add(keys)
        elif isinstance(keys, list):
            for key in keys:
                if isinstance(key, tuple):
                    self.indexes.add(key[0])
                else:
                    self.indexes.add(key)
    
    def _matches_filter(self, doc: Dict, filter_dict: Dict) -> bool:
        """Check if document matches filter"""
        if not filter_dict:
            return True
        
        for key, value in filter_dict.items():
            if key == "_id":
                # Handle ObjectId comparison
                if isinstance(value, ObjectId):
                    if str(doc.get("_id")) != str(value):
                        return False
                elif str(doc.get("_id")) != str(value):
                    return False
            elif key == "$or":
                # Handle $or operator
                if not any(self._matches_filter(doc, condition) for condition in value):
                    return False
            elif key == "$and":
                # Handle $and operator
                if not all(self._matches_filter(doc, condition) for condition in value):
                    return False
            elif key.endswith(".user_id"):
                # Handle nested field matching
                field_parts = key.split(".")
                if field_parts[0] in doc:
                    members = doc[field_parts[0]]
                    if isinstance(members, list):
                        if not any(str(member.get("user_id")) == str(value) for member in members):
                            return False
            elif "$ne" in str(value):
                # Handle $ne operator
                if isinstance(value, dict) and "$ne" in value:
                    if doc.get(key) == value["$ne"]:
                        return False
            elif "$regex" in str(value):
                # Handle regex matching
                if isinstance(value, dict) and "$regex" in value:
                    import re
                    pattern = value["$regex"]
                    flags = re.IGNORECASE if value.get("$options") == "i" else 0
                    if not re.search(pattern, str(doc.get(key, "")), flags):
                        return False
            elif "$in" in str(value):
                # Handle $in operator
                if isinstance(value, dict) and "$in" in value:
                    doc_value = doc.get(key)
                    if isinstance(doc_value, list):
                        if not any(item in value["$in"] for item in doc_value):
                            return False
                    else:
                        if doc_value not in value["$in"]:
                            return False
            else:
                if str(doc.get(key)) != str(value):
                    return False
        return True

class MockCursor:
    """Mock MongoDB cursor"""
    
    def __init__(self, collection: MockCollection, filter_dict: Dict, projection: Dict):
        self.collection = collection
        self.filter_dict = filter_dict or {}
        self.projection = projection
        self._skip_count = 0
        self._limit_count = None
    
    def skip(self, count: int):
        """Skip documents"""
        new_cursor = MockCursor(self.collection, self.filter_dict, self.projection)
        new_cursor._skip_count = count
        new_cursor._limit_count = self._limit_count
        return new_cursor
    
    def limit(self, count: int):
        """Limit documents"""
        new_cursor = MockCursor(self.collection, self.filter_dict, self.projection)
        new_cursor._skip_count = self._skip_count
        new_cursor._limit_count = count
        return new_cursor
    
    async def to_list(self, length: Optional[int] = None) -> List[Dict]:
        """Convert to list"""
        results = []
        for doc in self.collection.data.values():
            if self.collection._matches_filter(doc, self.filter_dict):
                result = doc.copy()
                if self.projection:
                    # Apply projection (simplified)
                    if any(v == 0 for v in self.projection.values()):
                        # Exclusion projection
                        for field, include in self.projection.items():
                            if include == 0 and field in result:
                                del result[field]
                results.append(result)
        
        # Apply skip and limit
        if self._skip_count:
            results = results[self._skip_count:]
        if self._limit_count:
            results = results[:self._limit_count]
        if length:
            results = results[:length]
        
        return results

class MockInsertResult:
    """Mock insert result"""
    def __init__(self, inserted_id: str):
        self.inserted_id = ObjectId(inserted_id)

class MockUpdateResult:
    """Mock update result"""
    def __init__(self, modified_count: int):
        self.modified_count = modified_count

class MockDeleteResult:
    """Mock delete result"""
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count

class MockDatabase:
    """Mock MongoDB database"""
    
    def __init__(self, name: str):
        self.name = name
        self.collections: Dict[str, MockCollection] = {}
        self.data_file = f"mock_db_{name}.json"
        self.load_data()
    
    def __getattr__(self, name: str) -> MockCollection:
        """Get collection by name"""
        if name not in self.collections:
            collection = MockCollection(name)
            collection.database = self  # Link collection to database
            self.collections[name] = collection
        return self.collections[name]
    
    def save_data(self):
        """Save all collections to JSON file"""
        try:
            data = {}
            for collection_name, collection in self.collections.items():
                # Convert ObjectId to string for JSON serialization
                collection_data = {}
                for doc_id, doc in collection.data.items():
                    doc_copy = doc.copy()
                    if '_id' in doc_copy and hasattr(doc_copy['_id'], '_id'):
                        doc_copy['_id'] = doc_copy['_id']._id
                    elif '_id' in doc_copy:
                        doc_copy['_id'] = str(doc_copy['_id'])
                    # Convert any datetime objects to strings
                    for key, value in doc_copy.items():
                        if isinstance(value, datetime):
                            doc_copy[key] = value.isoformat()
                    collection_data[doc_id] = doc_copy
                data[collection_name] = collection_data
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save mock database: {e}")
    
    def load_data(self):
        """Load collections from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                for collection_name, collection_data in data.items():
                    collection = MockCollection(collection_name)
                    collection.database = self  # Link collection to database
                    for doc_id, doc in collection_data.items():
                        # Convert string dates back to datetime objects
                        for key, value in doc.items():
                            if isinstance(value, str) and key.endswith(('_at', '_date')):
                                try:
                                    doc[key] = datetime.fromisoformat(value)
                                except:
                                    pass
                        # Ensure _id is ObjectId
                        if '_id' in doc:
                            doc['_id'] = ObjectId(doc['_id'])
                        collection.data[doc_id] = doc
                    self.collections[collection_name] = collection
                print(f"✅ Loaded persistent data from {self.data_file}")
        except Exception as e:
            print(f"Warning: Could not load mock database: {e}")

class MockClient:
    """Mock MongoDB client"""
    
    def __init__(self, *args, **kwargs):
        self.databases: Dict[str, MockDatabase] = {}
    
    def __getitem__(self, name: str) -> MockDatabase:
        """Get database by name"""
        if name not in self.databases:
            self.databases[name] = MockDatabase(name)
        return self.databases[name]
    
    async def admin_command(self, command: str):
        """Mock admin command"""
        if command == 'ping':
            return {"ok": 1}
        return {"ok": 1}
    
    def close(self):
        """Close connection"""
        pass

# Global mock database instance
mock_client = None
mock_database = None

async def init_mock_database():
    """Initialize mock database"""
    global mock_client, mock_database
    mock_client = MockClient()
    mock_database = mock_client["maomo_db"]
    
    # Create some test data
    await create_test_data()
    
    print("✅ Mock database initialized successfully")

async def create_test_data():
    """Create some initial test data"""
    # This will be called to populate test data
    pass

async def close_mock_database():
    """Close mock database"""
    global mock_client
    if mock_client:
        mock_client.close()
    print("Mock database connection closed")

def get_mock_database():
    """Get mock database instance"""
    return mock_database

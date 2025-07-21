from db.connect import client

try:
    # This will test the connection
    client.admin.command('ping')
    print("Database connection test successful!")
    
    # Print some basic database stats
    db = client["maomo"]
    collections = db.list_collection_names()
    print("\nAvailable collections:")
    for collection in collections:
        print(f"- {collection}: {db[collection].count_documents({})}")
        
except Exception as e:
    print("Database connection test failed!")
    print("Error:", str(e))
finally:
    client.close()

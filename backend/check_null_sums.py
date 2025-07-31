from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB credentials
mongodb_user = os.getenv('MONGODB_USER')
mongodb_password = os.getenv('MONGODB_PASSWORD')

# Connect to MongoDB using the same configuration as the app
uri = f"mongodb+srv://{mongodb_user}:{mongodb_password}@cluster0.qcym40v.mongodb.net/?retryWrites=true\u0026w=majority\u0026appName=Cluster0"
client = MongoClient(uri)
db = client['maomo']
note_collection = db['notes']
super_note_collection = db['supernotes']

print('=== CHECKING NOTES WITH NULL SUM FIELD ===')
null_sum_notes = list(note_collection.find({'Sum': None}))
print(f'Found {len(null_sum_notes)} notes with Sum = null')
for i, note in enumerate(null_sum_notes[:3]):
    header = note.get('Header', 'No Header')
    sum_val = note.get('Sum')
    print(f'Note {i+1}: Header={header}, Sum={sum_val}')

print('\n=== CHECKING SUPERNOTES WITH NULL SUM FIELD ===')
null_sum_supernotes = list(super_note_collection.find({'Sum': None}))
print(f'Found {len(null_sum_supernotes)} supernotes with Sum = null')
for i, supernote in enumerate(null_sum_supernotes[:3]):
    header = supernote.get('Header', 'No Header')
    sum_val = supernote.get('Sum')
    print(f'SuperNote {i+1}: Header={header}, Sum={sum_val}')

print('\n=== CHECKING FOR EMPTY OR MISSING SUM FIELDS ===')
empty_sum_notes = list(note_collection.find({'$or': [{'Sum': ''}, {'Sum': {'$exists': False}}]}))
print(f'Found {len(empty_sum_notes)} notes with empty or missing Sum field')

print('\n=== TOTAL NOTES AND SUPERNOTES ===')
total_notes = note_collection.count_documents({})
total_supernotes = super_note_collection.count_documents({})
print(f'Total notes: {total_notes}')
print(f'Total supernotes: {total_supernotes}')

client.close()

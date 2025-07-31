#!/usr/bin/env python3
"""
Script to fix null Sum fields in the database
This runs within the Flask app context to use existing database connections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.connect import note_collection, super_note_collection

def fix_null_sum_fields():
    """Fix null Sum fields by replacing them with empty strings"""
    
    print("=== FIXING NULL SUM FIELDS ===")
    
    # Fix notes with null Sum fields
    notes_result = note_collection.update_many(
        {'Sum': None},
        {'$set': {'Sum': ''}}
    )
    print(f"Updated {notes_result.modified_count} notes with null Sum fields")
    
    # Fix supernotes with null Sum fields
    supernotes_result = super_note_collection.update_many(
        {'Sum': None},
        {'$set': {'Sum': ''}}
    )
    print(f"Updated {supernotes_result.modified_count} supernotes with null Sum fields")
    
    print("\n=== VERIFICATION ===")
    
    # Verify the fix
    null_notes_count = note_collection.count_documents({'Sum': None})
    null_supernotes_count = super_note_collection.count_documents({'Sum': None})
    
    print(f"Remaining notes with null Sum: {null_notes_count}")
    print(f"Remaining supernotes with null Sum: {null_supernotes_count}")
    
    # Count total documents
    total_notes = note_collection.count_documents({})
    total_supernotes = super_note_collection.count_documents({})
    
    print(f"Total notes: {total_notes}")
    print(f"Total supernotes: {total_supernotes}")
    
    if null_notes_count == 0 and null_supernotes_count == 0:
        print("✅ All null Sum fields have been fixed!")
    else:
        print("❌ Some null Sum fields still remain")

if __name__ == "__main__":
    try:
        fix_null_sum_fields()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Flask app database connection is working properly.")

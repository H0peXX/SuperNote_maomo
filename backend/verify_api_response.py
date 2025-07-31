#!/usr/bin/env python3
"""
Script to verify what the API is returning for notes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.connect import note_collection, super_note_collection
from routes.user_route import mongo_to_json
import json

def verify_api_data():
    """Verify what data the API endpoints would return"""
    
    print("=== VERIFYING API DATA ===")
    
    # Get all notes (same as /api/notes endpoint)
    notes = list(note_collection.find({}))
    notes_json = mongo_to_json(notes)
    
    print(f"Total notes retrieved: {len(notes_json)}")
    
    # Check for any null Sum values
    null_sum_count = 0
    empty_sum_count = 0
    
    for i, note in enumerate(notes_json):
        sum_value = note.get('Sum')
        if sum_value is None:
            null_sum_count += 1
            print(f"Note {i+1}: Header='{note.get('Header', 'No Header')}', Sum=null")
        elif sum_value == '':
            empty_sum_count += 1
            print(f"Note {i+1}: Header='{note.get('Header', 'No Header')}', Sum='' (empty string)")
    
    print(f"\nSummary:")
    print(f"- Notes with Sum=null: {null_sum_count}")
    print(f"- Notes with Sum='' (empty): {empty_sum_count}")
    print(f"- Notes with content: {len(notes_json) - null_sum_count - empty_sum_count}")
    
    # Show a sample of the first few notes
    print(f"\n=== SAMPLE OF FIRST 3 NOTES ===")
    for i, note in enumerate(notes_json[:3]):
        print(f"Note {i+1}:")
        print(f"  Header: {note.get('Header', 'No Header')}")
        print(f"  Sum: {repr(note.get('Sum'))}")  # repr shows exact value including None
        print(f"  Topic: {note.get('Topic', 'No Topic')}")
        print()

if __name__ == "__main__":
    try:
        verify_api_data()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

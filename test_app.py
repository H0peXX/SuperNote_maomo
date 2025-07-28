#!/usr/bin/env python3
"""
Test script for SuperNote Flask application
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_signup():
    """Test user signup"""
    print("Testing signup...")
    data = {
        "username": "testuser",
        "email": "test@example.com", 
        "password": "testpass123",
        "fname": "Test",
        "lname": "User",
        "dob": "1990-01-01"
    }
    
    response = requests.post(f"{BASE_URL}/api/signup", json=data)
    print(f"Signup response: {response.status_code}")
    print(f"Response body: {response.json()}")
    return response.status_code == 201

def test_login():
    """Test user login"""
    print("\nTesting login...")
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/login", json=data)
    print(f"Login response: {response.status_code}")
    result = response.json()
    print(f"Response body: {result}")
    
    if response.status_code == 200:
        return result.get("access_token")
    return None

def test_create_summary(token):
    """Test creating a summary"""
    print("\nTesting create summary...")
    data = {
        "text": "This is a test article about artificial intelligence and machine learning. AI is revolutionizing many industries and changing how we work and live.",
        "header": "AI Test Summary",
        "topic": "Technology",
        "provider": "testuser"
    }
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.post(f"{BASE_URL}/save", json=data, headers=headers)
    print(f"Create summary response: {response.status_code}")
    print(f"Response body: {response.json()}")
    return response.status_code == 200

def test_get_summaries(token):
    """Test getting all summaries"""
    print("\nTesting get summaries...")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    response = requests.get(f"{BASE_URL}/api/notes", headers=headers)
    print(f"Get summaries response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {len(result.get('notes', []))} summaries")
        return result.get('notes', [])
    else:
        print(f"Error: {response.json()}")
        return []

if __name__ == "__main__":
    print("SuperNote Flask App Test")
    print("=" * 40)
    
    # Test signup
    signup_success = test_signup()
    
    # Test login
    token = test_login()
    
    if token:
        print(f"\nLogin successful! Token: {token[:20]}...")
        
        # Test create summary
        create_success = test_create_summary(token)
        
        # Test get summaries
        summaries = test_get_summaries(token)
        
        print(f"\nTest Results:")
        print(f"- Signup: {'✓' if signup_success else '✗'}")
        print(f"- Login: {'✓' if token else '✗'}")
        print(f"- Create Summary: {'✓' if create_success else '✗'}")
        print(f"- Get Summaries: {'✓' if summaries else '✗'}")
    else:
        print("\nLogin failed - cannot proceed with other tests")

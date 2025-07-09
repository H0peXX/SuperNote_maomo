import requests
import streamlit as st
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    """Client for communicating with the backend API"""
    
    def __init__(self):
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.session = requests.Session()
    
    def set_token(self, token: str):
        """Set the authentication token"""
        self.session.headers.update({
            "Authorization": f"Bearer {token}"
        })
    
    def clear_token(self):
        """Clear the authentication token"""
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
    
    def request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make a request to the API"""
        try:
            response = self.session.request(
                method, 
                f"{self.base_url}{endpoint}", 
                **kwargs
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                st.session_state.authenticated = False
                st.session_state.token = None
                st.session_state.user = None
                st.error("Session expired. Please log in again.")
                st.rerun()
            
            return response
            
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
            return None
    
    def get(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make a GET request"""
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make a POST request"""
        return self.request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make a PUT request"""
        return self.request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make a DELETE request"""
        return self.request("DELETE", endpoint, **kwargs)
    
    # Authentication endpoints
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Login user"""
        response = self.post("/api/auth/login", json={
            "email": email,
            "password": password
        })
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def register(self, username: str, email: str, full_name: str, password: str) -> Optional[Dict[str, Any]]:
        """Register new user"""
        response = self.post("/api/auth/register", json={
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password
        })
        
        if response and response.status_code == 201:
            return response.json()
        return None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user info"""
        response = self.get("/api/auth/me")
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    # Teams endpoints
    def get_teams(self) -> Optional[list]:
        """Get user teams"""
        response = self.get("/api/teams/")
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def create_team(self, name: str, description: str = "") -> Optional[Dict[str, Any]]:
        """Create new team"""
        response = self.post("/api/teams/", json={
            "name": name,
            "description": description
        })
        
        if response and response.status_code == 201:
            return response.json()
        return None
    
    def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get team details"""
        response = self.get(f"/api/teams/{team_id}")
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    # AI endpoints
    def process_pdf(self, file_content: bytes, language: str = "English", operation: str = "format") -> Optional[Dict[str, Any]]:
        """Process PDF file"""
        files = {"file": file_content}
        data = {
            "language": language,
            "operation": operation
        }
        
        response = self.post("/api/ai/process-pdf", files=files, data=data)
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def format_text(self, text: str, language: str = "English") -> Optional[Dict[str, Any]]:
        """Format text"""
        response = self.post("/api/ai/format-text", json={
            "text": text,
            "language": language,
            "operation": "format"
        })
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def summarize_text(self, text: str, language: str = "English") -> Optional[Dict[str, Any]]:
        """Summarize text"""
        response = self.post("/api/ai/summarize", json={
            "text": text,
            "language": language,
            "operation": "summarize"
        })
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def fact_check_text(self, text: str, language: str = "English") -> Optional[Dict[str, Any]]:
        """Fact check text"""
        response = self.post("/api/ai/fact-check", json={
            "text": text,
            "language": language,
            "operation": "fact_check"
        })
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def generate_quiz(self, text: str, language: str = "English") -> Optional[Dict[str, Any]]:
        """Generate quiz"""
        response = self.post("/api/ai/generate-quiz", json={
            "text": text,
            "language": language,
            "operation": "quiz"
        })
        
        if response and response.status_code == 200:
            return response.json()
        return None

# Global API client instance
api_client = APIClient()

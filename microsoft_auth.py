"""
Microsoft OAuth authentication and Todo API integration
"""
import os
import json
from typing import Optional, List, Dict
import requests
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

load_dotenv()

# Microsoft OAuth endpoints
AUTHORITY = "https://login.microsoftonline.com/common"
OAUTH_AUTHORIZE_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/authorize"
OAUTH_TOKEN_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/token"
GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"

# OAuth scopes for Microsoft Graph
SCOPES = [
    "Tasks.Read",
    "Tasks.ReadWrite",
    "offline_access"
]


class MicrosoftOAuthManager:
    """Manages Microsoft OAuth authentication"""
    
    def __init__(self):
        self.client_id = os.getenv('MICROSOFT_CLIENT_ID')
        self.client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')
        self.redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI', 'http://localhost:8000/callback')
        self.token_cache_file = 'config/microsoft_token.json'
        self.access_token = None
        self.token_data = None
        
        if not self.client_id or not self.client_secret:
            raise ValueError("MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET must be set in .env")
    
    def get_authorization_url(self) -> tuple:
        """Generate the Microsoft OAuth authorization URL"""
        oauth = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=SCOPES,
            authority=AUTHORITY
        )
        authorization_url, state = oauth.authorization_url(OAUTH_AUTHORIZE_ENDPOINT)
        return authorization_url, state
    
    def get_token_from_code(self, code: str, state: str) -> bool:
        """Exchange authorization code for access token"""
        try:
            token_data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri,
                'scope': ' '.join(SCOPES)
            }
            
            response = requests.post(OAUTH_TOKEN_ENDPOINT, data=token_data)
            response.raise_for_status()
            
            self.token_data = response.json()
            self.access_token = self.token_data.get('access_token')
            
            # Cache the token
            self._save_token()
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"Error obtaining token: {e}")
            return False
    
    def load_cached_token(self) -> bool:
        """Load cached token from file"""
        try:
            if os.path.exists(self.token_cache_file):
                with open(self.token_cache_file, 'r') as f:
                    self.token_data = json.load(f)
                    self.access_token = self.token_data.get('access_token')
                    return True
        except Exception as e:
            print(f"Error loading cached token: {e}")
        
        return False
    
    def _save_token(self):
        """Save token to cache file"""
        try:
            os.makedirs(os.path.dirname(self.token_cache_file), exist_ok=True)
            with open(self.token_cache_file, 'w') as f:
                json.dump(self.token_data, f)
        except Exception as e:
            print(f"Error saving token: {e}")
    
    def refresh_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.token_data or 'refresh_token' not in self.token_data:
            return False
        
        try:
            token_data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.token_data['refresh_token'],
                'scope': ' '.join(SCOPES)
            }
            
            response = requests.post(OAUTH_TOKEN_ENDPOINT, data=token_data)
            response.raise_for_status()
            
            self.token_data = response.json()
            self.access_token = self.token_data.get('access_token')
            self._save_token()
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def get_headers(self) -> Dict:
        """Get authorization headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }


class MicrosoftTodoAPI:
    """Interface to Microsoft Todo API"""
    
    def __init__(self, oauth_manager: MicrosoftOAuthManager):
        self.oauth = oauth_manager
        self.endpoint = GRAPH_API_ENDPOINT
    
    def get_task_lists(self) -> List[Dict]:
        """Get all task lists"""
        try:
            response = requests.get(
                f"{self.endpoint}/me/todo/lists",
                headers=self.oauth.get_headers()
            )
            response.raise_for_status()
            return response.json().get('value', [])
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching task lists: {e}")
            return []
    
    def get_tasks_from_list(self, list_id: str) -> List[Dict]:
        """Get all tasks from a specific list"""
        try:
            response = requests.get(
                f"{self.endpoint}/me/todo/lists/{list_id}/tasks",
                headers=self.oauth.get_headers()
            )
            response.raise_for_status()
            return response.json().get('value', [])
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching tasks: {e}")
            return []
    
    def get_important_tasks(self) -> List[Dict]:
        """Get tasks from the 'Important' list"""
        lists = self.get_task_lists()
        important_list = next((l for l in lists if l.get('displayName') == 'Important'), None)
        
        if not important_list:
            print("Error: 'Important' list not found")
            return []
        
        return self.get_tasks_from_list(important_list['id'])
    
    def get_starred_tasks(self) -> List[Dict]:
        """
        Get all starred tasks across all lists
        Note: Starred tasks are marked with importance='high'
        """
        try:
            response = requests.get(
                f"{self.endpoint}/me/todo/tasks?$filter=importance eq 'high'",
                headers=self.oauth.get_headers()
            )
            response.raise_for_status()
            return response.json().get('value', [])
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching starred tasks: {e}")
            return []

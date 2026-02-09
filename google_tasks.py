"""
Google Tasks API integration for fetching tasks
"""
import os
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import pickle
import json

load_dotenv()

# Google Tasks API scopes
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']


class GoogleTasksAuthManager:
    """Manages Google authentication for Tasks API"""
    
    def __init__(self):
        self.credentials_file = os.getenv('GOOGLE_TASKS_CREDENTIALS', 'config/google_credentials.json')
        self.token_cache_file = 'config/google_tasks_token.pkl'
        self.credentials = None
    
    def get_credentials(self) -> Optional[object]:
        """Get valid credentials for Google Tasks API"""
        
        # Try to load cached token first
        if os.path.exists(self.token_cache_file):
            with open(self.token_cache_file, 'rb') as token:
                self.credentials = pickle.load(token)
                if self.credentials.valid:
                    return self.credentials
                elif self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self._save_credentials()
                    return self.credentials
        
        # If no valid credentials, use OAuth2 flow
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Google credentials file not found at {self.credentials_file}. "
                "Please download it from Google Cloud Console and save it there."
            )
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, SCOPES)
            # Use http://localhost:8080/callback as the redirect URI
            # This matches what should be in Google Cloud Console
            self.credentials = flow.run_local_server(
                port=8080, 
                open_browser=True,
                authorization_prompt_message='Please visit this URL: {url}'
            )
        except OSError as e:
            if "Address already in use" in str(e):
                print("\n⚠️  Port 8080 is already in use")
                print("=" * 60)
                print("The app needs port 8080 to be available for Google OAuth.")
                print("\nOptions:")
                print("1. Stop whatever is using port 8080")
                print("2. Restart your computer to free up ports")
                print("3. Run: python main.py sync")
                print("=" * 60)
            raise
        except Exception as e:
            error_msg = str(e)
            if "redirect_uri_mismatch" in error_msg or "doesn't comply" in error_msg:
                print("\n⚠️  Google OAuth Configuration Issue")
                print("=" * 60)
                print("The redirect URI in your Google Cloud Console is not configured correctly.")
                print("\nTo fix:")
                print("1. Go to: https://console.cloud.google.com/apis/credentials")
                print("2. Find your OAuth 2.0 Desktop application credentials")
                print("3. Click the edit button (pencil icon)")
                print("4. Under 'Authorized redirect URIs', make sure you have:")
                print("   http://localhost:8080/callback")
                print("\n5. If it's not there, click 'ADD URI' and add it")
                print("6. Click SAVE")
                print("\nThen delete the cache and try again:")
                print("   rm config/google_tasks_token.pkl")
                print("   python main.py sync")
                print("=" * 60)
            raise
        
        # Save credentials for future use
        self._save_credentials()
        
        return self.credentials
    
    def _save_credentials(self):
        """Save credentials to file for future reuse"""
        os.makedirs('config', exist_ok=True)
        with open(self.token_cache_file, 'wb') as token:
            pickle.dump(self.credentials, token)


class GoogleTasksAPI:
    """Interface for Google Tasks API"""
    
    def __init__(self):
        self.auth_manager = GoogleTasksAuthManager()
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Tasks service"""
        credentials = self.auth_manager.get_credentials()
        self.service = build('tasks', 'v1', credentials=credentials)
    
    def get_all_tasklists(self) -> List[Dict]:
        """Get all task lists"""
        try:
            result = self.service.tasklists().list().execute()
            return result.get('items', [])
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def get_tasks_from_list(self, tasklist_id: str, show_completed: bool = False) -> List[Dict]:
        """Get all tasks from a specific task list"""
        try:
            result = self.service.tasks().list(
                tasklist=tasklist_id,
                showCompleted=show_completed,
                showHidden=True
            ).execute()
            return result.get('items', [])
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def get_tasks_by_due_date(self, tasklist_id: str, due_date: str) -> List[Dict]:
        """Get tasks due on a specific date (YYYY-MM-DD format)"""
        try:
            result = self.service.tasks().list(
                tasklist=tasklist_id,
                dueDate=due_date,
                showCompleted=False
            ).execute()
            return result.get('items', [])
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def get_important_tasks(self, max_results: int = 50) -> List[Dict]:
        """
        Get important/starred tasks from all lists
        Returns a flat list of tasks
        """
        all_tasks = []
        
        try:
            # Get all task lists
            tasklists = self.get_all_tasklists()
            
            for tasklist in tasklists:
                tasklist_id = tasklist['id']
                tasklist_title = tasklist.get('title', 'Unknown')
                
                # Get tasks from this list
                tasks = self.get_tasks_from_list(tasklist_id, show_completed=False)
                
                # Filter for important tasks (we'll use tasks with high priority indicators)
                for task in tasks:
                    task['tasklist_name'] = tasklist_title
                    task['tasklist_id'] = tasklist_id
                    all_tasks.append(task)
            
            # Sort by due date and title
            all_tasks.sort(key=lambda x: (
                x.get('due', 'z'),  # Tasks with due dates come first
                x.get('title', '')
            ))
            
            return all_tasks[:max_results]
        
        except Exception as e:
            print(f"Error getting important tasks: {e}")
            return []
    
    def get_default_tasklist(self) -> Optional[str]:
        """Get the ID of the default/primary task list"""
        try:
            tasklists = self.get_all_tasklists()
            if tasklists:
                # Return the first task list (usually the default)
                return tasklists[0]['id']
            return None
        except Exception as e:
            print(f"Error getting default task list: {e}")
            return None

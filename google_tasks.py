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
        
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, SCOPES)
        self.credentials = flow.run_local_server(port=0)
        
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

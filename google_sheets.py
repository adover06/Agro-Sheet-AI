"""
Google Sheets integration for syncing schedules
"""
import os
import json
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from schedule_models import WeeklySchedule, DailySchedule
from dotenv import load_dotenv
import json as json_module

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsManager:
    """Manages Google Sheets API integration"""
    
    def __init__(self):
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'config/google_credentials.json')
        self.token_file = 'config/sheets_token.json'  # Cache OAuth token here
        self.service = None
        
        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_ID must be set in .env")
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API with token caching"""
        try:
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(f"Credentials file not found at {self.credentials_file}")
            
            # Load credentials file and check if it's OAuth or Service Account
            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)
            
            credentials = None
            
            # Check if it's an OAuth credentials file (has 'web' key or 'client_id')
            if 'web' in creds_data or ('client_id' in creds_data and 'client_secret' in creds_data):
                # OAuth Desktop Flow - Check for cached token first
                from google.oauth2.credentials import Credentials as OAuthCredentials
                
                # Try to load cached token
                if os.path.exists(self.token_file):
                    credentials = OAuthCredentials.from_authorized_user_file(self.token_file, SCOPES)
                
                # If no valid credentials, get new ones
                if not credentials or not credentials.valid:
                    if credentials and credentials.expired and credentials.refresh_token:
                        # Refresh the expired token
                        credentials.refresh(Request())
                    else:
                        # Run OAuth flow for first-time authentication
                        # Use prompt='consent' to force Google to send a refresh token
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file,
                            SCOPES
                        )
                        credentials = flow.run_local_server(
                            port=8080, 
                            open_browser=False,
                            prompt='consent'  # Force consent to get refresh_token
                        )
                    
                    # Save the credentials for future runs
                    with open(self.token_file, 'w') as token:
                        token.write(credentials.to_json())
                    print(f"✓ OAuth token saved to {self.token_file}")
                
                self.service = build('sheets', 'v4', credentials=credentials)
                
            elif 'type' in creds_data and creds_data['type'] == 'service_account':
                # Service Account Flow (no caching needed - uses service account key directly)
                self.service = build(
                    'sheets',
                    'v4',
                    credentials=service_account.Credentials.from_service_account_file(
                        self.credentials_file,
                        scopes=SCOPES
                    )
                )
            else:
                raise ValueError("Credentials file format not recognized. Must be OAuth 2.0 or Service Account JSON.")
        
        except Exception as e:
            print(f"Error authenticating with Google Sheets: {e}")
            raise
    
    def sync_schedule_to_sheets(self, schedule: WeeklySchedule, color_scheme: Dict, start_cell: str = "A1") -> bool:
        """
        Sync weekly schedule to Google Sheets
        Updates 7 columns (Mon-Sun) with schedule data
        
        Args:
            schedule: WeeklySchedule object
            color_scheme: Dict with color definitions
            start_cell: Starting cell reference (e.g., "C22") where schedule will be pasted
        """
        try:
            # Prepare data for each day
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            # Parse start cell to get row and column offsets
            start_col, start_row = self._parse_cell_reference(start_cell)
            
            # Get all values to update
            values = self._prepare_sheet_values(schedule, day_order, color_scheme)
            
            # Calculate end cell reference
            end_col = chr(ord('A') + start_col + 6)  # 7 columns for days
            end_row = start_row + len(values)
            range_str = f"{start_cell}:{end_col}{end_row}"
            
            # Update the sheet
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_str,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Apply colors to cells
            self._apply_colors_to_sheet(schedule, day_order, color_scheme, start_col, start_row)
            
            print(f"Successfully synced schedule to Google Sheets")
            return True
        
        except HttpError as error:
            print(f"An error occurred with Google Sheets: {error}")
            return False
        except Exception as e:
            print(f"Error syncing schedule: {e}")
            return False
    
    def _parse_cell_reference(self, cell_ref: str) -> tuple:
        """
        Parse a cell reference like 'C22' into column index and row number
        Returns (column_index, row_number) where column_index is 0-based
        """
        import re
        match = re.match(r'([A-Z]+)(\d+)', cell_ref.upper())
        if not match:
            return (0, 1)  # Default to A1
        
        col_str, row_str = match.groups()
        
        # Convert column letters to index (A=0, B=1, etc.)
        col_idx = 0
        for char in col_str:
            col_idx = col_idx * 26 + (ord(char) - ord('A'))
        
        return (col_idx, int(row_str))
    
    def _prepare_sheet_values(self, schedule: WeeklySchedule, day_order: List[str], color_scheme: Dict) -> List[List]:
        """
        Prepare values for sheet update
        Format: 31 rows (1 header + 30 time blocks) x 7 columns (days)
        """
        values = []
        
        # Header row with day names
        header = day_order
        values.append(header)
        
        # Time blocks (9 AM to midnight = 30 blocks)
        time_blocks_data = self._get_all_time_blocks(schedule, day_order)
        
        for block_idx in range(30):
            row = []
            for day_idx, day_name in enumerate(day_order):
                if block_idx < len(time_blocks_data[day_name]):
                    block = time_blocks_data[day_name][block_idx]
                    # Only show task name, no timestamp
                    cell_value = block['task'] if block['task'] else ""
                    row.append(cell_value)
                else:
                    row.append("")
            values.append(row)
        
        return values
    
    def _get_all_time_blocks(self, schedule: WeeklySchedule, day_order: List[str]) -> Dict[str, List[Dict]]:
        """
        Extract all time blocks from schedule
        """
        blocks_data = {}
        
        for day_name in day_order:
            daily_schedule = schedule.schedules.get(day_name)
            blocks_data[day_name] = []
            
            if daily_schedule:
                for block in daily_schedule.blocks:
                    blocks_data[day_name].append({
                        'time': f"{block.start_time}-{block.end_time}",
                        'task': block.task_name or "",
                        'category': block.category,
                        'color': block.color
                    })
        
        return blocks_data
    
    def _apply_colors_to_sheet(self, schedule: WeeklySchedule, day_order: List[str], color_scheme: Dict, 
                                start_col: int = 0, start_row: int = 1):
        """
        Apply background colors to cells based on task category
        Uses Google Sheets batchUpdate API
        
        Args:
            start_col: Column offset (0-based)
            start_row: Row offset (1-based)
        """
        try:
            requests = []
            day_col_map = {day: col for col, day in enumerate(day_order)}
            
            for day_name in day_order:
                daily_schedule = schedule.schedules.get(day_name)
                if not daily_schedule:
                    continue
                
                col_idx = day_col_map[day_name] + start_col
                
                for block_idx, block in enumerate(daily_schedule.blocks):
                    # Row index: start_row is 1-based, convert to 0-based for API, +1 for header
                    row_idx = (start_row - 1) + block_idx + 1
                    
                    # Normalize category to lowercase for matching
                    category = (block.category or 'unscheduled').lower()
                    
                    # Map common category variations
                    category_map = {
                        'project': 'projects',
                        'break': 'breaks',
                        'fixed': 'fixed_events',
                        'empty': 'unscheduled'
                    }
                    category = category_map.get(category, category)
                    
                    if category in color_scheme.get('color_scheme', {}):
                        color_hex = color_scheme['color_scheme'][category]['hex']
                        rgb = self._hex_to_rgb_normalized(color_hex)
                        
                        requests.append({
                            'repeatCell': {
                                'range': {
                                    'sheetId': 0,  # Assuming first sheet
                                    'startRowIndex': row_idx,
                                    'startColumnIndex': col_idx,
                                    'endRowIndex': row_idx + 1,
                                    'endColumnIndex': col_idx + 1
                                },
                                'cell': {
                                    'userEnteredFormat': {
                                        'backgroundColor': {
                                            'red': rgb[0],
                                            'green': rgb[1],
                                            'blue': rgb[2]
                                        }
                                    }
                                },
                                'fields': 'userEnteredFormat.backgroundColor'
                            }
                        })
            
            if requests:
                body = {'requests': requests}
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=body
                ).execute()
                print(f"Applied colors to {len(requests)} cells")
        
        except Exception as e:
            print(f"Warning: Could not apply colors to sheet: {e}")
    
    @staticmethod
    def _hex_to_rgb_normalized(hex_color: str) -> tuple:
        """
        Convert hex color to RGB normalized (0.0 to 1.0)
        """
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)

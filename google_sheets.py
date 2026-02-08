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
        self.service = None
        
        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_ID must be set in .env")
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Try to use service account credentials first
            if os.path.exists(self.credentials_file):
                self.service = build(
                    'sheets',
                    'v4',
                    credentials=service_account.Credentials.from_service_account_file(
                        self.credentials_file,
                        scopes=SCOPES
                    )
                )
            else:
                raise FileNotFoundError(f"Credentials file not found at {self.credentials_file}")
        
        except Exception as e:
            print(f"Error authenticating with Google Sheets: {e}")
            raise
    
    def sync_schedule_to_sheets(self, schedule: WeeklySchedule, color_scheme: Dict) -> bool:
        """
        Sync weekly schedule to Google Sheets
        Updates 7 columns (Mon-Sun) with schedule data
        """
        try:
            # Prepare data for each day
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            # Get all values to update
            values = self._prepare_sheet_values(schedule, day_order, color_scheme)
            
            # Update the sheet
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range="A1:G31",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Apply colors to cells
            self._apply_colors_to_sheet(schedule, day_order, color_scheme)
            
            print(f"Successfully synced schedule to Google Sheets")
            return True
        
        except HttpError as error:
            print(f"An error occurred with Google Sheets: {error}")
            return False
        except Exception as e:
            print(f"Error syncing schedule: {e}")
            return False
    
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
                    cell_value = f"{block['time']}\n{block['task']}" if block['task'] else block['time']
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
    
    def _apply_colors_to_sheet(self, schedule: WeeklySchedule, day_order: List[str], color_scheme: Dict):
        """
        Apply background colors to cells based on task category
        Uses Google Sheets batchUpdate API
        """
        try:
            requests = []
            day_col_map = {day: col for col, day in enumerate(day_order)}
            
            for day_name in day_order:
                daily_schedule = schedule.schedules.get(day_name)
                if not daily_schedule:
                    continue
                
                col_idx = day_col_map[day_name]
                
                for row_idx, block in enumerate(daily_schedule.blocks, start=1):  # start=1 for header
                    if block.category in color_scheme['color_scheme']:
                        color_hex = color_scheme['color_scheme'][block.category]['hex']
                        rgb = self._hex_to_rgb_normalized(color_hex)
                        
                        requests.append({
                            'repeatCell': {
                                'range': {
                                    'sheetId': 0,  # Assuming first sheet
                                    'rowIndex': row_idx,
                                    'columnIndex': col_idx,
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

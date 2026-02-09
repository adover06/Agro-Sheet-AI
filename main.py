"""
Main CLI application for Daily Schedule AI Orchestrator
Now using Google Tasks and Gemini Pro
"""
import os
import sys
import json
import yaml
import click
from datetime import datetime, timedelta
from dotenv import load_dotenv

from schedule_models import create_empty_schedule, save_schedule_to_json, WeeklySchedule
from task_parser import parse_task_from_todo, parse_time_from_text, categorize_task
from config_loader import load_fixed_events_config
from fixed_events_placement import place_fixed_events
from gemini_scheduling import GeminiSchedulingAgent
from google_tasks import GoogleTasksAPI
from google_sheets import GoogleSheetsManager

load_dotenv()


@click.group()
def cli():
    """Daily Schedule AI Orchestrator - Sync your tasks and events into a perfect schedule"""
    pass


@cli.command()
@click.option('--day', type=click.Choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']), help='Specific day to schedule')
@click.option('--debug', is_flag=True, help='Use cached data instead of calling APIs')
def sync(day, debug):
    """Sync tasks from Google Tasks and generate schedule using Gemini AI"""
    try:
        click.echo("🔄 Starting schedule synchronization...")
        if debug:
            click.echo("🐛 DEBUG MODE ACTIVATED: Using cached data")
        
        # Step 1 & 2: Authenticate and Fetch tasks
        tasks = []
        if debug and os.path.exists('tasks_cache.json'):
            click.echo("\n📋 Loading tasks from cache...")
            with open('tasks_cache.json', 'r') as f:
                tasks_data = json.load(f)
                # Reconstruct Task objects from dictionary if needed, or just use as is if compatible
                # For simplicity in this flow, we might need to adjust or validat
                # But actually, we need Task objects for the scheduler. 
                # Let's assume we cache the raw todo_items or parsed tasks.
                # Let's cache the parsed tasks data.
                from schedule_models import Task
                tasks = [Task(**t) for t in tasks_data]
            click.echo(f"✓ Loaded {len(tasks)} tasks from cache")
            
        elif not debug:
            click.echo("\n📝 Authenticating with Google Tasks...")
            try:
                tasks_api = GoogleTasksAPI()
                click.echo("✓ Google Tasks authenticated")
                
                click.echo("\n📋 Fetching tasks from Google Tasks...")
                todo_items = tasks_api.get_important_tasks()
                
                if not todo_items:
                    click.echo("Warning: No tasks found in Google Tasks")
                    todo_items = []
                else:
                    click.echo(f"✓ Found {len(todo_items)} tasks")
                
                # Step 3: Parse tasks
                click.echo("\n🔍 Parsing tasks...")
                tasks = [parse_task_from_todo(item) for item in todo_items]
                click.echo(f"✓ Parsed {len(tasks)} tasks")
                
                # Cache tasks for debug mode
                with open('tasks_cache.json', 'w') as f:
                    # Convert tasks to dicts for JSON serialization
                    json.dump([t.__dict__ for t in tasks], f, indent=2)
                    
            except Exception as e:
                click.echo(f"Error: Google Tasks failed - {e}", err=True)
                sys.exit(1)
        else:
            click.echo("Error: Debug mode enabled but no cache found. Run without --debug first.", err=True)
            sys.exit(1)
        
        # Step 4: Load fixed events configuration
        click.echo("\n📅 Loading fixed events configuration...")
        fixed_events_config = load_fixed_events_config('config/fixed_events.yaml')
        click.echo(f"✓ Loaded {len(fixed_events_config)} fixed events")
        
        # Step 5: Create and populate schedule
        # In debug mode, if we have a full schedule output, we might want to skip this?
        # But we might want to re-run placement logic. 
        # Actually, let's load the FULL schedule from json if in debug mode to save Gemini calls.
        
        schedule = None
        if debug and os.path.exists('schedule_output.json'):
             click.echo("\n🗓️ Loading schedule from cache (skipping Gemini)...")
             from schedule_models import WeeklySchedule, DailySchedule, TimeBlock
             
             with open('schedule_output.json', 'r') as f:
                 schedule_data = json.load(f)
                 
             # Reconstruct WeeklySchedule object
             schedule = create_empty_schedule()
             schedule.week_start_date = schedule_data.get('week_start_date')
             
             for day_name, day_data in schedule_data.get('days', {}).items():
                 if day_name in schedule.schedules:
                     # Reconstruct blocks
                     blocks = []
                     for b_data in day_data.get('blocks', []):
                         block = TimeBlock(start_time=b_data['time'].split('-')[0], end_time=b_data['time'].split('-')[1])
                         block.task_name = b_data.get('task')
                         block.category = b_data.get('category')
                         block.is_flexible = b_data.get('is_flexible', False)
                         block.color = b_data.get('color')
                         blocks.append(block)
                     schedule.schedules[day_name].blocks = blocks
             
             click.echo("✓ Schedule loaded from cache")

        else:
            # Normal flow or valid cache was not found/usable
            click.echo("\n🗓️ Creating schedule structure...")
            schedule = create_empty_schedule()
            
            # Set week start date
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            schedule.week_start_date = week_start.strftime("%Y-%m-%d")
            
            click.echo("✓ Schedule structure created")
            
            # Step 6: Place fixed events
            click.echo("\n🔧 Placing fixed events...")
            schedule, flexible_events = place_fixed_events(schedule, fixed_events_config)
            click.echo(f"✓ Placed fixed events")
            if flexible_events:
                click.echo(f"  - {len(flexible_events)} flexible events to place intelligently")
            
            # Step 7: Run Gemini scheduling agent
            if not debug:
                click.echo("\n🤖 Running Gemini AI scheduling agent...")
                try:
                    agent = GeminiSchedulingAgent(schedule)
                    success = agent.schedule_tasks(tasks, flexible_events)
                    
                    if success:
                        click.echo("✓ Tasks scheduled successfully")
                    else:
                        click.echo("Warning: Some tasks could not be scheduled", err=True)
                except Exception as e:
                    click.echo(f"Error: Gemini scheduling failed - {e}", err=True)
                    sys.exit(1)
            
        # Step 8: Load color scheme
        click.echo("\n🎨 Loading color scheme...")
        with open('config/color_scheme.json', 'r') as f:
            color_scheme = json.load(f)
        click.echo("✓ Color scheme loaded")
        
        # Step 9: Save to local JSON (updating cache if we just ran)
        if not debug:
            click.echo("\n💾 Saving schedule to local JSON...")
            save_schedule_to_json(schedule, 'schedule_output.json')
            click.echo("✓ Saved to schedule_output.json")
        
        # Step 10: Sync to Google Sheets
        click.echo("\n📊 Syncing to Google Sheets...")
        try:
             # Get start_cell and sheet_name from config
            with open('config/fixed_events.yaml', 'r') as f:
                config = yaml.safe_load(f)
            google_sheets_config = config.get('google_sheets', {})
            start_cell = google_sheets_config.get('start_cell', 'A1')
            sheet_name = google_sheets_config.get('sheet_name')
            
            sheets_manager = GoogleSheetsManager()
            if sheets_manager.sync_schedule_to_sheets(schedule, color_scheme, start_cell=start_cell, sheet_name=sheet_name):
                click.echo("✓ Successfully synced to Google Sheets")
            else:
                click.echo("Error: Failed to sync to Google Sheets", err=True)
        except Exception as e:
            click.echo(f"Error: Google Sheets sync failed - {e}", err=True)
        
        click.echo("\n✅ Schedule synchronization complete!")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def setup_oauth():
    """Set up Google Tasks API credentials"""
    try:
        click.echo("🔐 Google Tasks Setup")
        click.echo("=" * 40)
        
        credentials_path = click.prompt(
            "Enter path to your Google credentials JSON file",
            default="config/google_credentials.json"
        )
        
        # Verify credentials file exists
        if not os.path.exists(credentials_path):
            click.echo(f"Warning: Credentials file not found at {credentials_path}", err=True)
            click.echo("Please download it from Google Cloud Console:")
            click.echo("1. Go to https://console.cloud.google.com/")
            click.echo("2. Create a new project or select existing one")
            click.echo("3. Enable Google Tasks API")
            click.echo("4. Create OAuth 2.0 Desktop credentials")
            click.echo("5. Download the JSON file and save to the path above")
        
        # Update .env file
        with open('.env', 'a') as f:
            f.write(f"\nGOOGLE_TASKS_CREDENTIALS={credentials_path}\n")
        
        click.echo("✓ Google Tasks configuration saved to .env")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def setup_google_sheets():
    """Set up Google Sheets integration"""
    try:
        click.echo("📊 Google Sheets Setup")
        click.echo("=" * 40)
        
        sheets_id = click.prompt("Enter your Google Sheets ID (from the URL)")
        credentials_path = click.prompt("Enter path to your Google credentials JSON file", default="config/google_credentials.json")
        
        # Verify credentials file exists
        if not os.path.exists(credentials_path):
            click.echo(f"Warning: Credentials file not found at {credentials_path}", err=True)
            click.echo("Please download your credentials from Google Cloud Console")
        
        # Update .env file
        with open('.env', 'a') as f:
            f.write(f"\nGOOGLE_SHEETS_ID={sheets_id}\n")
            f.write(f"GOOGLE_SHEETS_CREDENTIALS={credentials_path}\n")
        
        click.echo("✓ Google Sheets configuration saved to .env")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def setup_openai():
    """Set up Gemini Pro API key"""
    try:
        click.echo("🔑 Gemini Pro API Setup")
        click.echo("=" * 40)
        
        api_key = click.prompt("Enter your Gemini Pro API key")
        
        with open('.env', 'a') as f:
            f.write(f"\nGEMINI_API_KEY={api_key}\n")
        
        click.echo("✓ Gemini Pro API key saved to .env")
        click.echo("\nYou can get your Gemini API key at:")
        click.echo("https://makersuite.google.com/app/apikey")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def view_schedule():
    """View the current schedule from saved JSON"""
    try:
        if not os.path.exists('schedule_output.json'):
            click.echo("Error: No schedule found. Run 'sync' first.", err=True)
            sys.exit(1)
        
        with open('schedule_output.json', 'r') as f:
            schedule = json.load(f)
        
        click.echo("📅 Weekly Schedule")
        click.echo("=" * 80)
        
        for day_name, day_data in schedule.get('days', {}).items():
            click.echo(f"\n{day_name.upper()}")
            click.echo("-" * 80)
            
            for block in day_data.get('blocks', []):
                time_range = block.get('time', '')
                task = block.get('task', 'Free')
                category = block.get('category', '')
                
                if task:
                    click.echo(f"  {time_range} | {task} [{category}]")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()

"""
Main CLI application for Daily Schedule AI Orchestrator
"""
import os
import sys
import json
import click
from datetime import datetime, timedelta
from dotenv import load_dotenv

from schedule_models import create_empty_schedule, save_schedule_to_json, WeeklySchedule
from task_parser import parse_task_from_todo, parse_time_from_text, categorize_task
from config_loader import load_fixed_events_config
from fixed_events_placement import place_fixed_events
from scheduling_agent import SchedulingAgent
from microsoft_auth import MicrosoftOAuthManager, MicrosoftTodoAPI
from google_sheets import GoogleSheetsManager

load_dotenv()


@click.group()
def cli():
    """Daily Schedule AI Orchestrator - Sync your tasks and events into a perfect schedule"""
    pass


@cli.command()
@click.option('--day', type=click.Choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']), help='Specific day to schedule')
def sync(day):
    """Sync tasks from Microsoft Todo and generate schedule"""
    try:
        click.echo("🔄 Starting schedule synchronization...")
        
        # Step 1: Authenticate with Microsoft
        click.echo("\n📝 Authenticating with Microsoft Todo...")
        oauth_manager = MicrosoftOAuthManager()
        
        # Try to load cached token first
        if not oauth_manager.load_cached_token():
            click.echo("No cached credentials found. Please authenticate...")
            auth_url, state = oauth_manager.get_authorization_url()
            click.echo(f"Please visit this URL to authorize: {auth_url}")
            
            auth_code = click.prompt("Enter the authorization code from the redirect URL")
            if not oauth_manager.get_token_from_code(auth_code, state):
                click.echo("Error: Failed to obtain access token", err=True)
                sys.exit(1)
        else:
            click.echo("✓ Using cached credentials")
        
        # Step 2: Fetch tasks from Microsoft Todo
        click.echo("\n📋 Fetching starred tasks from Microsoft Todo...")
        todo_api = MicrosoftTodoAPI(oauth_manager)
        todo_items = todo_api.get_important_tasks()
        
        if not todo_items:
            click.echo("Warning: No tasks found in Important list")
            todo_items = []
        else:
            click.echo(f"✓ Found {len(todo_items)} tasks")
        
        # Step 3: Parse tasks
        click.echo("\n🔍 Parsing tasks...")
        tasks = [parse_task_from_todo(item) for item in todo_items]
        click.echo(f"✓ Parsed {len(tasks)} tasks")
        
        # Step 4: Load fixed events configuration
        click.echo("\n📅 Loading fixed events configuration...")
        fixed_events_config = load_fixed_events_config('config/fixed_events.yaml')
        click.echo(f"✓ Loaded {len(fixed_events_config)} fixed events")
        
        # Step 5: Create and populate schedule
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
        
        # Step 7: Run scheduling agent
        click.echo("\n🤖 Running intelligent scheduling agent...")
        agent = SchedulingAgent(schedule)
        success = agent.schedule_tasks(tasks, flexible_events)
        
        if success:
            click.echo("✓ Tasks scheduled successfully")
        else:
            click.echo("Warning: Some tasks could not be scheduled", err=True)
        
        # Step 8: Load color scheme
        click.echo("\n🎨 Loading color scheme...")
        with open('config/color_scheme.json', 'r') as f:
            color_scheme = json.load(f)
        click.echo("✓ Color scheme loaded")
        
        # Step 9: Save to local JSON
        click.echo("\n💾 Saving schedule to local JSON...")
        save_schedule_to_json(schedule, 'schedule_output.json')
        click.echo("✓ Saved to schedule_output.json")
        
        # Step 10: Sync to Google Sheets
        click.echo("\n📊 Syncing to Google Sheets...")
        try:
            sheets_manager = GoogleSheetsManager()
            if sheets_manager.sync_schedule_to_sheets(schedule, color_scheme):
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
    """Set up Microsoft OAuth credentials"""
    try:
        click.echo("🔐 Microsoft OAuth Setup")
        click.echo("=" * 40)
        
        client_id = click.prompt("Enter your Microsoft Client ID")
        client_secret = click.prompt("Enter your Microsoft Client Secret")
        redirect_uri = click.prompt("Enter your redirect URI", default="http://localhost:8000/callback")
        
        # Update .env file
        env_content = f"""MICROSOFT_CLIENT_ID={client_id}
MICROSOFT_CLIENT_SECRET={client_secret}
MICROSOFT_REDIRECT_URI={redirect_uri}
"""
        
        with open('.env', 'a') as f:
            f.write(env_content)
        
        click.echo("✓ OAuth credentials saved to .env")
        
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
    """Set up OpenAI API key"""
    try:
        click.echo("🔑 OpenAI API Setup")
        click.echo("=" * 40)
        
        api_key = click.prompt("Enter your OpenAI API key")
        
        with open('.env', 'a') as f:
            f.write(f"\nOPENAI_API_KEY={api_key}\n")
        
        click.echo("✓ OpenAI API key saved to .env")
        
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

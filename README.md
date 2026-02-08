# Daily Schedule AI Orchestrator

A Python CLI tool that intelligently schedules your tasks from Microsoft Todo, combines them with your fixed events, and syncs everything to a Google Sheets calendar.

## Features

- **Microsoft Todo Integration**: Fetches starred tasks from your "Important" list
- **Intelligent Scheduling**: Uses an AI agent to schedule tasks based on your preferences (night owl, project bias)
- **Fixed Events**: YAML-based configuration for classes, recurring activities, and flexible daily obligations
- **Time-Aware Parsing**: Automatically detects time constraints in task titles (e.g., "morning run 9-10am")
- **Task Splitting**: Automatically splits tasks longer than 2 hours
- **Google Sheets Sync**: Updates your weekly schedule spreadsheet with color-coded blocks
- **Local Export**: Saves schedule as JSON for testing and reference

## Project Structure

```
Agro-Sheet/
├── main.py                      # CLI entry point
├── schedule_models.py           # Data structures for schedules and tasks
├── task_parser.py              # Task parsing and time extraction utilities
├── config_loader.py            # YAML configuration loader
├── fixed_events_placement.py   # Fixed events scheduling logic
├── scheduling_agent.py         # Intelligent scheduling agent
├── microsoft_auth.py           # Microsoft OAuth and Todo API integration
├── google_sheets.py            # Google Sheets API integration
├── config/
│   ├── fixed_events.yaml       # Your fixed events configuration
│   ├── color_scheme.json       # Color coding for tasks
│   └── google_credentials.json # Google API credentials (download from Google Cloud)
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with:
- `MICROSOFT_CLIENT_ID`: Your Microsoft OAuth Client ID
- `MICROSOFT_CLIENT_SECRET`: Your Microsoft OAuth Client Secret
- `GOOGLE_SHEETS_ID`: Your Google Sheets spreadsheet ID
- `OPENAI_API_KEY`: Your OpenAI API key (for future LangChain integration)

### 3. Configure Fixed Events

Edit `config/fixed_events.yaml` to add your classes, recurring events, and flexible daily activities:

```yaml
fixed_events:
  - name: "Math Class"
    days: ["Monday", "Wednesday", "Friday"]
    start_time: "09:00"
    end_time: "10:30"
    flexible: false
    category: "school"
  
  - name: "Morning Prayer"
    days: ["Daily"]
    duration: 30
    flexible: true  # Agent will place this intelligently
    category: "personal"
```

### 4. Set Up Google Sheets API

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google Sheets API
3. Create a Service Account and download the JSON credentials file
4. Place the credentials file at `config/google_credentials.json`
5. Share your Google Sheet with the service account email

### 5. Set Up Microsoft OAuth

1. Register an app in [Microsoft Azure Portal](https://portal.azure.com/)
2. Create OAuth credentials (Client ID and Secret)
3. Note your Application ID and create a client secret
4. Add `http://localhost:8000/callback` as a redirect URI

## Usage

### Synchronize Schedule

```bash
python main.py sync
```

This will:
1. Authenticate with Microsoft Todo (or use cached credentials)
2. Fetch your starred tasks
3. Parse tasks and detect time constraints
4. Place fixed events in the schedule
5. Use the scheduling agent to intelligently place tasks
6. Save to `schedule_output.json`
7. Sync to your Google Sheets

### View Current Schedule

```bash
python main.py view-schedule
```

### Interactive Setup Commands

```bash
# Set up Microsoft OAuth
python main.py setup-oauth

# Set up Google Sheets
python main.py setup-google-sheets

# Set up OpenAI API
python main.py setup-openai
```

## How It Works

### Task Parsing

The system parses your Microsoft Todo tasks and:
- Detects time constraints in titles (e.g., "morning run 9-10am")
- Estimates duration based on keywords and task description
- Categorizes tasks as "projects", "school", or "personal"
- Respects the "Important" list for task selection

### Intelligent Scheduling

The `SchedulingAgent` places tasks based on:
- **Night Owl Preference**: Favors later time slots (after 3 PM)
- **Project Bias**: Allocates better time slots for project work vs. school
- **Time Constraints**: Places time-constrained tasks at specified times
- **Task Importance**: High-importance tasks get priority
- **Task Splitting**: Tasks over 2 hours are split into 2 parts

### Fixed Events

Fixed events are placed in the schedule with:
- **Fixed-Time Events**: Classes, appointments placed at exact times
- **Flexible Events**: Activities like prayer, cooking, breaks are placed intelligently
- **Daily Recurrence**: Use "Daily" to repeat events every day
- **Specific Days**: List specific days for weekly events

### Color Coding

Edit `config/color_scheme.json` to customize colors for different task types:
- Projects: Blue
- School: Red
- Personal: Green
- Breaks: Yellow
- Fixed Events: Gray

## Schedule Format

The schedule is organized as:
- **7 days** (Monday - Sunday)
- **30 blocks per day** (30 minutes each)
- **Time range**: 9:00 AM to 12:00 AM (midnight)
- **Output**: JSON format locally + Google Sheets

Each block contains:
- Time range (e.g., "09:00-09:30")
- Task name
- Category (projects, school, personal, breaks, fixed_events)
- Color code

## Google Sheets Layout

Your spreadsheet will have:
- **Columns**: Monday through Sunday
- **Rows**: 30 time blocks + header row
- **Colors**: Automatically applied based on task category
- **Updates**: Overwrites existing data for the current day

## Troubleshooting

### "Important" list not found
Make sure you have a list named exactly "Important" in your Microsoft Todo account. The system pulls from this list specifically.

### Tasks not getting scheduled
Check the console output for warnings about task conflicts. Tasks longer than 2 hours will be split or skipped if they can't fit.

### Google Sheets not updating
Verify that:
1. The credentials file is correct and accessible
2. The service account email has access to your spreadsheet
3. The `GOOGLE_SHEETS_ID` environment variable is set correctly

### Token refresh issues
Delete `config/microsoft_token.json` to force re-authentication on next run.

## Future Enhancements

- LangChain agent for more sophisticated scheduling decisions
- Natural language task parsing
- Calendar integration (Outlook, Google Calendar)
- Web dashboard
- Recurring task support
- Task estimation based on historical data

## License

MIT

## Support

For issues or feedback, please visit: https://github.com/anomalyco/opencode

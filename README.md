# Daily Schedule AI Orchestrator

A Python CLI tool that intelligently schedules your tasks from Google Tasks using AI, combines them with your fixed events, and syncs everything to a Google Sheets calendar.

## Features

- **Google Tasks Integration**: Fetches tasks from your Google Tasks lists
- **Gemini Pro AI**: Uses Google's Gemini Pro model for intelligent scheduling
- **Fixed Events**: YAML-based configuration for classes, recurring activities, and flexible daily obligations
- **Time-Aware Parsing**: Automatically detects time constraints in task titles (e.g., "morning run 9-10am")
- **Task Splitting**: Automatically splits tasks longer than 2 hours
- **Google Sheets Sync**: Updates your weekly schedule spreadsheet with color-coded blocks
- **Local Export**: Saves schedule as JSON for testing and reference
- **No Subscriptions**: Uses free Google services and Gemini Pro API

## Project Structure

```
Agro-Sheet/
├── main.py                      # CLI entry point
├── schedule_models.py           # Data structures for schedules and tasks
├── task_parser.py              # Task parsing and time extraction utilities
├── config_loader.py            # YAML configuration loader
├── fixed_events_placement.py   # Fixed events scheduling logic
├── gemini_scheduling.py        # Gemini Pro-powered scheduling agent
├── google_tasks.py             # Google Tasks API integration
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

### 2. Set Up Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Tasks API** and **Google Sheets API**
4. Create OAuth 2.0 Desktop credentials
5. Download JSON and save to `config/google_credentials.json`

### 3. Get Gemini Pro API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Save for later setup

### 4. Run Setup Commands

```bash
# Setup Google Tasks credentials
python main.py setup-oauth

# Setup Gemini Pro API key
python main.py setup-openai

# Setup Google Sheets (optional)
python main.py setup-google-sheets
```

### 5. Configure Fixed Events

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

## Usage

### Synchronize Schedule

```bash
python main.py sync
```

This will:
1. Authenticate with Google Tasks
2. Fetch your tasks
3. Parse tasks and detect time constraints
4. Place fixed events in the schedule
5. Use Gemini Pro AI to intelligently place tasks
6. Save to `schedule_output.json`
7. Sync to your Google Sheets (if configured)

### View Current Schedule

```bash
python main.py view-schedule
```

### Interactive Setup Commands

```bash
# Set up Google Tasks
python main.py setup-oauth

# Set up Google Sheets
python main.py setup-google-sheets

# Set up Gemini Pro
python main.py setup-openai
```

## How It Works

### Task Parsing

The system parses your Google Tasks and:
- Detects time constraints in titles (e.g., "morning run 9-10am")
- Estimates duration based on keywords and task description
- Categorizes tasks as "projects", "school", or "personal"
- Extracts due dates and importance indicators

### Intelligent Scheduling with Gemini Pro

The `GeminiSchedulingAgent` uses Google's Gemini Pro model to:
- Analyze all your tasks and their characteristics
- Determine optimal scheduling order using natural language understanding
- Consider priorities, deadlines, and task categories
- Respect preferences for night owl schedules
- Allocate better time slots for project work vs. school

**Preferences:**
- **Night Owl Schedule**: Favors later time slots (after 12 PM)
- **Project Bias**: Better time slots for project work
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

### Tasks not appearing
- Verify you have tasks in Google Tasks
- Check that Google credentials are valid
- Verify credentials file is at `config/google_credentials.json`

### Gemini API errors
- Verify `GEMINI_API_KEY` is set correctly in `.env`
- Check that API key has access at https://makersuite.google.com/app/apikey

### Google Sheets not updating
Verify that:
1. The credentials file is correct and accessible
2. The `GOOGLE_SHEETS_ID` environment variable is set correctly
3. The sheet is shared with your Google account

## Environment Variables

After setup, your `.env` will contain:

```env
GOOGLE_TASKS_CREDENTIALS=config/google_credentials.json
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_SHEETS_CREDENTIALS=config/google_credentials.json
GEMINI_API_KEY=your_gemini_api_key
```

## Future Enhancements

- Multi-turn conversations with Gemini for task clarification
- Smart task duration estimation using AI
- Real-time task updates from Google Tasks
- Integration with Google Calendar for automatic fixed events
- Web dashboard for schedule management
- Recurring task support

## License

MIT

## Support

For issues or feedback, please visit: https://github.com/anomalyco/opencode

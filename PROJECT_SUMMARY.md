# Daily Schedule AI Orchestrator - Project Summary

## Overview

You now have a complete Python CLI application that intelligently schedules your tasks from Microsoft Todo, combines them with fixed events (classes, recurring obligations), and syncs everything to Google Sheets with color coding.

## What's Been Built

### Core Features Implemented ✅

1. **Microsoft Todo Integration** (`microsoft_auth.py`, `main.py`)
   - OAuth 2.0 authentication with caching
   - Fetches tasks from "Important" list
   - Supports starred/high-priority tasks

2. **Intelligent Task Scheduling** (`scheduling_agent.py`)
   - Night owl preference (favors later time slots after 3 PM)
   - Project > School bias (allocates better times for projects)
   - Time-aware parsing (respects "9-10am" format in task titles)
   - Smart task splitting (splits tasks > 2 hours into 2 parts)
   - Task categorization (projects, school, personal)

3. **Fixed Events Management** (`config_loader.py`, `fixed_events_placement.py`)
   - YAML-based configuration
   - Fixed-time events (classes at specific times)
   - Flexible events (prayer, cooking, breaks placed intelligently)
   - Daily and weekly recurrence patterns

4. **Schedule Structure** (`schedule_models.py`)
   - 7 days × 30 time blocks (9 AM to midnight)
   - 30-minute block granularity
   - Color-coded categorization
   - JSON export for local storage

5. **Google Sheets Sync** (`google_sheets.py`)
   - Writes schedule to spreadsheet
   - Updates 7 columns (Mon-Sun) × 30 rows
   - Applies color coding per task category
   - Uses Service Account authentication

6. **Task Parsing** (`task_parser.py`)
   - Extracts time constraints from task titles
   - Estimates duration based on keywords
   - Auto-categorizes tasks
   - Rounds times to nearest 30-minute block

7. **CLI Interface** (`main.py`)
   - `python main.py sync` - Full synchronization
   - `python main.py view-schedule` - View current schedule
   - `python main.py setup-oauth` - Configure Microsoft
   - `python main.py setup-google-sheets` - Configure Google
   - `python main.py setup-openai` - Configure OpenAI API

8. **Demo Mode** (`demo.py`)
   - Test scheduling without Microsoft authentication
   - Create sample schedule with demo tasks
   - Useful for validating setup

### Configuration Files

- **`config/fixed_events.yaml`** - Your classes and recurring events
- **`config/color_scheme.json`** - Task color customization
- **`.env.example`** - Environment variables template
- **`requirements.txt`** - Python dependencies

### Documentation

- **`README.md`** - Comprehensive documentation
- **`QUICKSTART.md`** - Step-by-step setup guide
- **`PROJECT_SUMMARY.md`** - This file

## File Structure

```
Agro-Sheet/
├── Python Modules
│   ├── main.py                      # CLI entry point (230+ lines)
│   ├── schedule_models.py           # Data structures (160+ lines)
│   ├── task_parser.py              # Task parsing utilities (170+ lines)
│   ├── scheduling_agent.py         # Intelligent scheduling (380+ lines)
│   ├── microsoft_auth.py           # Microsoft OAuth & API (220+ lines)
│   ├── google_sheets.py            # Google Sheets API (240+ lines)
│   ├── config_loader.py            # Configuration loader (70+ lines)
│   ├── fixed_events_placement.py   # Fixed events logic (60+ lines)
│   └── demo.py                     # Demo mode (140+ lines)
│
├── Configuration
│   ├── config/
│   │   ├── fixed_events.yaml       # Your schedule template
│   │   └── color_scheme.json       # Task colors
│   ├── .env.example                # Environment setup
│   └── requirements.txt            # Dependencies
│
├── Documentation
│   ├── README.md                   # Full documentation
│   ├── QUICKSTART.md              # Quick setup guide
│   └── PROJECT_SUMMARY.md         # This file
│
└── Runtime Files (generated)
    ├── .env                        # Your credentials (YOU create)
    ├── config/google_credentials.json  # Google API key (YOU provide)
    ├── config/microsoft_token.json     # Microsoft token cache (auto-generated)
    ├── schedule_output.json            # Your schedule (auto-generated)
    └── schedule_demo.json              # Demo schedule (auto-generated)
```

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Copy Environment Template

```bash
cp .env.example .env
```

### 3. Configure Credentials

**Microsoft OAuth:**
1. Register app at https://portal.azure.com/
2. Get Client ID and Secret
3. Add to `.env`

**Google Sheets:**
1. Create project at https://console.cloud.google.com/
2. Download service account JSON
3. Save as `config/google_credentials.json`
4. Add Sheets ID to `.env`

### 4. Configure Fixed Events

Edit `config/fixed_events.yaml`:
- Add your classes (fixed times)
- Add recurring activities (flexible placement)
- Daily obligations (prayer, cooking, breaks)

### 5. Run First Sync

```bash
python main.py sync
```

This will:
- Authenticate with Microsoft (first time only)
- Fetch your starred tasks
- Create your schedule
- Sync to Google Sheets
- Save to `schedule_output.json`

### 6. View Your Schedule

```bash
python main.py view-schedule
```

## Key Algorithms

### Task Scheduling Algorithm

1. **Sort tasks by priority** (high importance, projects > school, time-constrained)
2. **Place time-constrained tasks** (respect specified time ranges)
3. **Place flexible events** (intelligently across the week)
4. **Schedule remaining tasks** (use scoring function):
   - Preference for later times (night owl)
   - Better slots for projects vs. school
   - Isolation bonus for clear before/after blocks
5. **Handle long tasks** (split if > 2 hours, skip if too long)

### Time Parsing Logic

- Pattern: `"9-10am"`, `"9:30-10:30am"`, `"09:00-10:00"`
- Rounds to nearest 30-minute block
- Falls back to keyword-based duration estimation
- Categories by keywords: project, school, personal

### Scoring Function

Each potential time slot gets a score based on:
- **Hour preference**: +0.5 per hour (9am=0, midnight=7.5)
- **Category bias**: Projects +2.0, School +1.0, Personal +0.5
- **Isolation bonus**: +0.5 if no adjacent tasks

## Data Structures

### Task Object
```python
Task(
    id, title, description,
    importance, category,
    estimated_duration, has_time_constraint,
    constraint_start_time, constraint_end_time
)
```

### TimeBlock Object
```python
TimeBlock(
    start_time, end_time,
    task_name, category, color,
    is_flexible, duration_blocks
)
```

### DailySchedule
- 30 TimeBlocks per day
- 9 AM to midnight (15 hours = 30 × 30-min blocks)

### WeeklySchedule
- 7 DailySchedules (Mon-Sun)
- JSON export capability
- Week start date

## Google Sheets Format

Your spreadsheet will have:
- **Columns**: Monday through Sunday (A-G)
- **Rows**: 31 (header + 30 time blocks)
- **Cell Format**: "HH:MM-HH:MM\nTask Name"
- **Colors**: Automatically applied per category

Example:
```
Monday          | Tuesday        | Wednesday
9:00-9:30       | 9:00-9:30      | 9:00-9:30
9:30-10:00      | 9:30-10:00     | 9:30-10:00
Morning Prayer  | Morning Prayer | Morning Prayer
...
```

## Color Coding

Edit `config/color_scheme.json` to customize:
- **Projects**: Blue (#4A90E2)
- **School**: Red (#E74C3C)
- **Personal**: Green (#27AE60)
- **Breaks**: Yellow (#F39C12)
- **Fixed Events**: Gray (#95A5A6)

## Tips for Optimal Use

1. **Daily Sync**: Run `python main.py sync` each morning
2. **Task Timestamps**: Use "9-10am" format for specific times
3. **Keywords**: Include "project", "homework", "personal" for auto-categorization
4. **Flexible Events**: Adjust prayer/cooking times in `fixed_events.yaml`
5. **Check Google Sheet**: Verify sync worked with color codes

## Example Workflow

```
1. Morning: Add tasks to Microsoft Todo
2. Star/mark important the ones to schedule
3. Run: python main.py sync
4. Review schedule in Google Sheets
5. Adjust fixed events if needed
6. Repeat next day
```

## Technology Stack

- **Python 3.8+**
- **CLI**: Click
- **API Clients**: requests, google-api-python-client
- **Auth**: OAuth 2.0 (Microsoft + Google)
- **Config**: YAML, JSON
- **Data**: Dataclasses, JSON

## Future Enhancements

- [ ] LangChain integration for advanced scheduling
- [ ] Web dashboard for schedule visualization
- [ ] Calendar integration (Outlook, Google Calendar)
- [ ] Natural language task parsing
- [ ] Historical data analysis for better estimates
- [ ] Recurring task support with intervals
- [ ] Task dependencies and blocking
- [ ] Analytics and productivity tracking

## Troubleshooting

**"Important" list not found?**
- Create a list named "Important" in Microsoft Todo
- Make sure tasks are in that list

**Tasks not scheduled?**
- Check console warnings for task conflicts
- Verify fixed events aren't blocking slots
- Increase max_continuous_minutes in scheduling_agent.py

**Google Sheets not updating?**
- Verify service account has edit access
- Check GOOGLE_SHEETS_ID is correct
- Verify credentials file is valid JSON

**Time parsing issues?**
- Use format: "9-10am" or "09:00-10:00"
- No extra spaces: "9 - 10 am" won't work
- Use 24-hour for afternoon: "2-3pm" → "14:00-15:00"

## Support & Feedback

For issues or feature requests:
- Check the troubleshooting section
- Review console output for error messages
- Consult README.md for detailed docs
- Submit feedback at: https://github.com/anomalyco/opencode

## Project Statistics

- **Total Lines of Code**: ~1,800+
- **Number of Modules**: 8
- **Number of Classes**: 15+
- **Configuration Files**: 3
- **Documentation Pages**: 3
- **Time Blocks Supported**: 210 (30 per day × 7 days)
- **Task Categories**: 3 (projects, school, personal)
- **Color Schemes**: 5

## License

MIT - Feel free to modify and use as you wish!

---

**Your Daily Schedule AI Orchestrator is ready to go!** 🚀

Start with: `python main.py sync`

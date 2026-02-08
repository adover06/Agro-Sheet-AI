# Agro-Sheet Conversion: Google Tasks + Gemini Pro

## What Changed

This app has been completely converted from using Microsoft Todo and OpenAI to using **Google Tasks** and **Google Gemini Pro**.

### Key Changes

#### 1. **Task Management: Microsoft Todo → Google Tasks**
   - **New file**: `google_tasks.py` (replaces `microsoft_auth.py`)
   - Fetches tasks from Google Tasks API instead of Microsoft Graph
   - Simpler OAuth flow using Google's standard credentials
   - No need for expensive Azure subscriptions

#### 2. **AI Scheduling: OpenAI → Gemini Pro**
   - **New file**: `gemini_scheduling.py` (replaces `scheduling_agent.py`)
   - Uses Google's Gemini Pro model for intelligent task scheduling
   - More advanced AI-powered task ordering and placement
   - Better context understanding for optimal scheduling

#### 3. **Configuration Updates**
   - Updated `main.py` to use new Google APIs
   - Updated `requirements.txt` with new dependencies
   - Updated `.env.example` with new environment variables

## Setup Instructions

### 1. Get Google Credentials

You'll need one set of credentials for both Google Tasks and Google Sheets:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable these APIs:
   - Google Tasks API
   - Google Sheets API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Select "Desktop application"
6. Download the JSON file and save as `config/google_credentials.json`

### 2. Get Gemini Pro API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key
4. Copy the key for later

### 3. Setup the App

Run the setup commands:

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup Google Tasks
python main.py setup-oauth

# Setup Gemini Pro
python main.py setup-openai  # Despite the name, this now sets up Gemini

# Setup Google Sheets (optional, for syncing results)
python main.py setup-google-sheets
```

The commands will prompt you to:
- Enter path to Google credentials JSON
- Enter your Gemini API key
- Enter your Google Sheets ID (optional)

All values will be saved to `.env` file automatically.

## Usage

### Sync Tasks and Generate Schedule

```bash
python main.py sync
```

This will:
1. ✓ Authenticate with Google Tasks
2. ✓ Fetch your tasks
3. ✓ Parse task details
4. ✓ Load fixed events (meetings, breaks, etc.)
5. ✓ Use Gemini AI to intelligently schedule tasks
6. ✓ Save schedule to `schedule_output.json`
7. ✓ Optionally sync to Google Sheets

### View Your Schedule

```bash
python main.py view-schedule
```

This displays the generated schedule in the terminal.

## How It Works

### Google Tasks Integration
- Fetches all tasks from your Google Tasks lists
- Extracts task details (title, due date, notes)
- Parses time information from task descriptions

### Gemini AI Scheduling
The scheduling engine uses Gemini Pro to:
1. Analyze all your tasks
2. Consider priority, deadlines, and categories
3. Determine optimal scheduling order
4. Place tasks in your weekly schedule
5. Respect fixed events (meetings, breaks, etc.)

**Preferences:**
- Night owl schedule (prefers afternoon/evening for important work)
- Projects > School > Personal task hierarchy
- Time-sensitive tasks prioritized
- Consecutive work blocks up to 2 hours

### Google Sheets Sync
Optionally syncs your final schedule to Google Sheets for:
- Easy sharing
- Web access
- Calendar integration
- Color-coded visualization

## Environment Variables

After setup, your `.env` file will contain:

```env
# Google Tasks API
GOOGLE_TASKS_CREDENTIALS=config/google_credentials.json

# Google Sheets (optional)
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_SHEETS_CREDENTIALS=config/google_credentials.json

# Gemini Pro AI
GEMINI_API_KEY=your_gemini_api_key

# Schedule Configuration
SCHEDULE_START_HOUR=9
SCHEDULE_END_HOUR=24
BLOCK_DURATION_MINUTES=30
MAX_CONTINUOUS_TASK_MINUTES=120
```

## Troubleshooting

### "No module named 'google.auth'"
Make sure you've run:
```bash
pip install -r requirements.txt
```

### "Google credentials file not found"
Download your Google credentials JSON and save to `config/google_credentials.json`

### "GEMINI_API_KEY not found"
Make sure you've run `python main.py setup-openai` and entered your API key

### "No tasks found"
1. Make sure you have tasks in Google Tasks
2. Check that your Google credentials have Tasks API enabled
3. Verify the credentials file is correct

## Files Changed

**New:**
- `google_tasks.py` - Google Tasks API wrapper
- `gemini_scheduling.py` - Gemini-powered scheduler

**Updated:**
- `main.py` - New setup and sync commands
- `requirements.txt` - New dependencies (google-generativeai)
- `.env.example` - Updated environment variables

**Deleted (optional):**
- `microsoft_auth.py` - No longer needed
- `scheduling_agent.py` - Replaced by gemini_scheduling.py

## Dependencies

The new stack:
- `google-generativeai==0.3.0` - Gemini Pro API
- `google-api-python-client==2.107.0` - Google APIs (Tasks, Sheets)
- `google-auth-oauthlib==1.2.0` - Google OAuth
- `google-auth==2.27.0` - Google Auth library
- And supporting libraries (requests, pyyaml, click, etc.)

## Future Improvements

Some ideas for enhancements:
- Gemini multi-turn conversations for task clarification
- Smart task duration estimation using Gemini
- Real-time task updates from Google Tasks
- Integration with Google Calendar for fixed events
- Custom scheduling preferences via Gemini prompts

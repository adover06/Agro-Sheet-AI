# Quick Start Guide

## Prerequisites

- Python 3.8+
- Microsoft Account with Todo app
- Google Account with Google Sheets
- OpenAI API key (for future enhancements)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter issues with pip, you may need to use:
```bash
python -m pip install -r requirements.txt
```

## Step 2: Get Microsoft OAuth Credentials

1. Go to [Azure Portal](https://portal.azure.com/)
2. Click "App registrations" → "New registration"
3. Name it "Daily Schedule Orchestrator"
4. Set Redirect URI to: `http://localhost:8000/callback`
5. Go to "Certificates & secrets"
6. Create a new client secret and copy it
7. Copy your Application (Client) ID

## Step 3: Get Google Sheets Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Google Sheets API"
4. Create a Service Account:
   - Go to "Service Accounts"
   - Create new service account
   - Create a JSON key
   - Download and save as `config/google_credentials.json`
5. Share your Google Sheet with the service account email

## Step 4: Create Your Google Sheet

1. Create a new Google Sheet with 7 columns (Mon-Sun) and 31 rows (header + 30 time blocks)
2. Add headers in the first row: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
3. In column A, add time blocks (optional):
   - 9:00-9:30, 9:30-10:00, etc.
4. Copy the Sheet ID from the URL (it's the long string between `/d/` and `/edit`)

## Step 5: Configure Environment

1. Copy `.env.example` to `.env`
2. Fill in your credentials:

```
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_REDIRECT_URI=http://localhost:8000/callback
GOOGLE_SHEETS_ID=your_sheet_id
GOOGLE_SHEETS_CREDENTIALS=config/google_credentials.json
OPENAI_API_KEY=your_openai_key
```

## Step 6: Configure Your Fixed Events

Edit `config/fixed_events.yaml` with your classes and recurring events:

```yaml
fixed_events:
  # Your classes
  - name: "Math Class"
    days: ["Monday", "Wednesday", "Friday"]
    start_time: "09:00"
    end_time: "10:30"
    flexible: false
    is_free: false
    category: "school"

  # Daily obligations (flexible placement)
  - name: "Morning Prayer"
    days: ["Daily"]
    duration: 30
    flexible: true
    is_free: false
    category: "personal"

  - name: "Cooking Dinner"
    days: ["Daily"]
    duration: 60
    flexible: true
    is_free: false
    category: "personal"

  - name: "Breaks/Snacks"
    days: ["Daily"]
    duration: 15
    flexible: true
    is_free: true
    category: "break"
```

## Step 7: Prepare Your Microsoft Todo

1. Open Microsoft Todo
2. Create a list called "Important" (if not exists)
3. Star/mark important the tasks you want scheduled
4. These tasks will be pulled into your schedule

**Important**: Tasks with time in the title will be placed at that time. Examples:
- "morning run 9-10am" → scheduled for 9:00-10:00
- "Project work 2pm-4pm" → scheduled for 2:00 PM - 4:00 PM
- "afternoon study" → estimated duration, placed intelligently

## Step 8: Run Your First Sync

```bash
python main.py sync
```

You'll be prompted to authenticate with Microsoft if needed. The process will:
1. Fetch your tasks
2. Create your schedule
3. Save locally to `schedule_output.json`
4. Sync to your Google Sheet

## Customizing Colors

Edit `config/color_scheme.json` to change task colors:

```json
{
  "color_scheme": {
    "projects": {
      "hex": "#4A90E2",
      "rgb": [74, 144, 226]
    },
    "school": {
      "hex": "#E74C3C",
      "rgb": [231, 76, 60]
    },
    ...
  }
}
```

## Viewing Your Schedule

After syncing, view your schedule:

```bash
python main.py view-schedule
```

Or check `schedule_output.json` for raw data.

## Tips for Best Results

1. **Be specific with time constraints** - Use "9-10am" or "2:30-3:30pm" format in task titles
2. **Use categories** - Include keywords like "project:", "homework:", "personal:" to help categorization
3. **Regular updates** - Sync at the beginning of your day
4. **Edit fixed events** - Keep your `fixed_events.yaml` updated with your actual schedule
5. **Review your colors** - Customize color schemes in `color_scheme.json` to your preference

## Troubleshooting

**Authentication issues?**
- Delete `config/microsoft_token.json` and try again
- Make sure redirect URI matches exactly

**Tasks not showing up?**
- Check that they're in the "Important" list
- Make sure tasks aren't in a different list
- Check console for warnings

**Google Sheets not updating?**
- Verify credentials file is valid
- Make sure service account email has edit access
- Check GOOGLE_SHEETS_ID is correct

## What's Next?

1. Schedule your first day
2. Review the output in Google Sheets
3. Adjust fixed events as needed
4. Customize colors to your preference
5. Set up a cron job or scheduled task to sync daily

Enjoy your perfectly organized schedule! 🚀

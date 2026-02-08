# Setup Checklist

Complete this checklist to get your Daily Schedule AI Orchestrator up and running.

## Prerequisites
- [ ] Python 3.8 or higher installed
- [ ] Google account with Google Tasks
- [ ] Google account with Google Drive/Sheets (can be same account)
- [ ] Gemini Pro API key

## Step 1: Install Dependencies
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify installations completed without errors

## Step 2: Set Up Google Credentials
- [ ] Go to https://console.cloud.google.com/
- [ ] Create new project (or select existing)
- [ ] Enable "Google Tasks API"
- [ ] Enable "Google Sheets API"
- [ ] Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
- [ ] Select "Desktop application"
- [ ] Download JSON file
- [ ] Save to `config/google_credentials.json`

## Step 3: Get Gemini Pro API Key
- [ ] Go to https://makersuite.google.com/app/apikey
- [ ] Click "Get API Key"
- [ ] Create new API key
- [ ] Copy and keep it safe

## Step 4: Create .env File
- [ ] Copy `.env.example` to `.env`
- [ ] You'll populate this using setup commands (next step)

## Step 5: Run Setup Commands
- [ ] Run `python main.py setup-oauth`
  - Enter path to `config/google_credentials.json`
- [ ] Run `python main.py setup-openai`
  - Paste your Gemini Pro API key
- [ ] Run `python main.py setup-google-sheets` (optional)
  - Get your Google Sheet ID from the URL
  - Share sheet with your Google account

## Step 6: Configure Fixed Events
- [ ] Open `config/fixed_events.yaml`
- [ ] Add your classes (with specific times)
- [ ] Add your weekly recurring events
- [ ] Add daily obligations (prayer, cooking, breaks)
- [ ] Verify YAML syntax is correct

## Step 7: Prepare Google Tasks
- [ ] Open Google Tasks (tasks.google.com)
- [ ] Add tasks you want to schedule
- [ ] You can organize them into different lists
- [ ] (Optional) Add time in notes like "2-3pm" or "9:00-10:00"

## Step 8: Test the Setup
- [ ] Run `python main.py view-schedule` (should show empty/fixed events only)
- [ ] Run `python demo.py` (test with sample tasks)
- [ ] Review the output in `schedule_demo.json`

## Step 9: Run Your First Sync
- [ ] Run `python main.py sync`
- [ ] Wait for Gemini to analyze and schedule your tasks
- [ ] Review the output in terminal

## Step 10: Check Results
- [ ] Open `schedule_output.json` to see the schedule
- [ ] Run `python main.py view-schedule` to see formatted output
- [ ] Check your Google Sheet - should be updated with your schedule
- [ ] Verify tasks are color-coded correctly

## Step 11: Customize (Optional)
- [ ] Edit `config/color_scheme.json` to change colors if desired
- [ ] Run `python main.py sync` again to test new colors
- [ ] Update fixed events in YAML as needed
- [ ] Adjust task categories by adding keywords

## Step 12: Daily Usage
- [ ] Each morning, add tasks to Google Tasks
- [ ] Run `python main.py sync`
- [ ] Review your schedule in Google Sheets or terminal
- [ ] Done! Your day is perfectly scheduled

## Troubleshooting Checklist

### Authentication Issues
- [ ] Is the credentials file valid JSON?
- [ ] Did you copy the correct file to `config/google_credentials.json`?
- [ ] Is GEMINI_API_KEY set correctly in .env?

### Tasks Not Appearing
- [ ] Do you have tasks in Google Tasks?
- [ ] Check console output for error messages
- [ ] Verify credentials file is valid

### Google Sheets Not Updating
- [ ] Is the credentials file valid JSON?
- [ ] Does the Sheet ID match your actual spreadsheet?
- [ ] Is the sheet shared with your Google account?

### Schedule Looks Wrong
- [ ] Are fixed events properly configured in YAML?
- [ ] Do tasks have time format "HH:MM-HH:MM" (e.g., "9-10am") in notes?
- [ ] Are you using a recognized time format?
- [ ] Check the `schedule_output.json` for raw schedule data

## Quick Command Reference

```bash
# First sync - will prompt for authentication
python main.py sync

# View current schedule in terminal
python main.py view-schedule

# Test with demo data (no authentication needed)
python demo.py

# Interactive setup prompts
python main.py setup-oauth
python main.py setup-google-sheets
python main.py setup-openai
```

## Files You've Created

After setup, you should have:

```
config/
  ├── fixed_events.yaml          # ✓ Your configuration
  ├── color_scheme.json          # ✓ Color customization
  └── google_credentials.json    # ✓ Google API key

.env                             # ✓ Your credentials (created from .env.example)
config/microsoft_token.json      # (auto-created after first auth)
schedule_output.json             # (auto-created after first sync)
```

## You're All Set! 🎉

Your Daily Schedule AI Orchestrator is now ready to organize your life!

**Next Step**: Run `python main.py sync` to schedule your first day.

---

**Need Help?**
- Check `README.md` for comprehensive documentation
- See `QUICKSTART.md` for step-by-step guide
- Review `PROJECT_SUMMARY.md` for technical details
- Check console output for error messages

**Report Issues**: https://github.com/anomalyco/opencode

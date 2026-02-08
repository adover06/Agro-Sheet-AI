# Setup Checklist

Complete this checklist to get your Daily Schedule AI Orchestrator up and running.

## Prerequisites
- [ ] Python 3.8 or higher installed
- [ ] Microsoft account with Microsoft Todo
- [ ] Google account with Google Drive/Sheets
- [ ] OpenAI account (for future enhancements)

## Step 1: Install Dependencies
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify installations completed without errors

## Step 2: Set Up Microsoft OAuth
- [ ] Go to https://portal.azure.com/
- [ ] Create app registration for "Daily Schedule Orchestrator"
- [ ] Copy Client ID to safe location
- [ ] Create client secret and copy it
- [ ] Set Redirect URI to: `http://localhost:8000/callback`
- [ ] Keep these credentials safe - you'll need them next

## Step 3: Create .env File
- [ ] Copy `.env.example` to `.env`
- [ ] Add Microsoft Client ID from Step 2
- [ ] Add Microsoft Client Secret from Step 2
- [ ] Add Redirect URI: `http://localhost:8000/callback`

## Step 4: Set Up Google Sheets API
- [ ] Go to https://console.cloud.google.com/
- [ ] Create new project
- [ ] Enable "Google Sheets API"
- [ ] Create Service Account
- [ ] Generate JSON key from service account
- [ ] Download and save to `config/google_credentials.json`
- [ ] Copy service account email

## Step 5: Create Google Sheet
- [ ] Create new Google Sheet
- [ ] Add headers: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
- [ ] (Optional) Add time labels in first column: 9:00-9:30, 9:30-10:00, etc.
- [ ] Copy Sheet ID from URL
- [ ] Add to `.env` as `GOOGLE_SHEETS_ID`
- [ ] Share sheet with service account email from Step 4

## Step 6: Set Up .env File (Complete)
- [ ] `MICROSOFT_CLIENT_ID` = Your Microsoft client ID
- [ ] `MICROSOFT_CLIENT_SECRET` = Your Microsoft client secret
- [ ] `MICROSOFT_REDIRECT_URI` = `http://localhost:8000/callback`
- [ ] `GOOGLE_SHEETS_ID` = Your Google Sheet ID
- [ ] `GOOGLE_SHEETS_CREDENTIALS` = `config/google_credentials.json`
- [ ] `OPENAI_API_KEY` = Your OpenAI API key (optional for now)

## Step 7: Configure Fixed Events
- [ ] Open `config/fixed_events.yaml`
- [ ] Add your classes (with specific times)
- [ ] Add your weekly recurring events
- [ ] Add daily obligations (prayer, cooking, breaks)
- [ ] Verify YAML syntax is correct

## Step 8: Create "Important" List in Microsoft Todo
- [ ] Open Microsoft Todo
- [ ] Create a list named "Important" (exactly this name)
- [ ] This is where you'll star tasks to be scheduled

## Step 9: Test the Setup
- [ ] Run `python main.py view-schedule` (should show empty/fixed events only)
- [ ] Run `python demo.py` (test with sample tasks)
- [ ] Review the output in `schedule_demo.json`

## Step 10: Add Tasks and Sync
- [ ] Open Microsoft Todo
- [ ] Add some test tasks with time markers (e.g., "Project work 2-3pm")
- [ ] Star/mark important the tasks you want in your schedule
- [ ] Run `python main.py sync`
- [ ] First time will prompt for Microsoft authentication - follow the link
- [ ] Enter the authorization code when prompted
- [ ] Review the output

## Step 11: Check Results
- [ ] Open `schedule_output.json` to see the schedule
- [ ] Run `python main.py view-schedule` to see formatted output
- [ ] Check your Google Sheet - should be updated with your schedule
- [ ] Verify tasks are color-coded correctly

## Step 12: Customize (Optional)
- [ ] Edit `config/color_scheme.json` to change colors if desired
- [ ] Run `python main.py sync` again to test new colors
- [ ] Update fixed events in YAML as needed
- [ ] Adjust task categories by adding keywords

## Step 13: Daily Usage
- [ ] Each morning, add tasks to Microsoft Todo
- [ ] Star the tasks you want to schedule
- [ ] Run `python main.py sync`
- [ ] Review your schedule in Google Sheets
- [ ] Done! Your day is perfectly scheduled

## Troubleshooting Checklist

### Authentication Issues
- [ ] Are Client ID and Secret correct?
- [ ] Is Redirect URI exactly: `http://localhost:8000/callback`?
- [ ] Did you delete `config/microsoft_token.json` to force re-auth?

### Tasks Not Appearing
- [ ] Is there a list named "Important" in Microsoft Todo?
- [ ] Are tasks actually starred/marked important?
- [ ] Check console output for error messages

### Google Sheets Not Updating
- [ ] Is the credentials file valid JSON?
- [ ] Does the Sheet ID match your actual spreadsheet?
- [ ] Has the service account email been added as editor?
- [ ] Is the sheet publicly readable (or shared with service account)?

### Schedule Looks Wrong
- [ ] Are fixed events properly configured in YAML?
- [ ] Do tasks have time format "HH:MM-HH:MM" (e.g., "9-10am")?
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

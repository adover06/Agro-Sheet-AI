# Quick Start: Google Tasks + Gemini Pro

## 1. Get Your Credentials

### Google Credentials (for Tasks API)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable: **Google Tasks API** and **Google Sheets API**
4. Create OAuth 2.0 Desktop credentials
5. Download JSON and save as `config/google_credentials.json`

### Gemini Pro API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Copy the key

## 2. Setup (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Setup Google Tasks (follow the prompt)
python main.py setup-oauth

# Setup Gemini (paste your API key)
python main.py setup-openai

# Optional: Setup Google Sheets
python main.py setup-google-sheets
```

## 3. Run It!

```bash
python main.py sync
```

This will:
- ✓ Fetch your tasks from Google Tasks
- ✓ Use Gemini AI to schedule them intelligently
- ✓ Save to `schedule_output.json`
- ✓ Sync to Google Sheets (if configured)

## 4. View Your Schedule

```bash
python main.py view-schedule
```

That's it! 🎉

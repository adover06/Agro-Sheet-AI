# Fix: Google OAuth Configuration Issue

## Problem
You're getting this error:
```
You can't sign in to this app because it doesn't comply with Google's OAuth 2.0 policy.
redirect_uri=http://localhost:XXXXX/
```

## Root Cause
The redirect URI in your Google Cloud Console credentials is not configured correctly. Google requires an exact match.

## Solution

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/apis/credentials
2. Look for your "OAuth 2.0 Client ID" (should say "Desktop application")

### Step 2: Edit Your Credentials
1. Click the **pencil icon** to edit the credentials

### Step 3: Add the Correct Redirect URI
1. Under "Authorized redirect URIs", you'll see a text area
2. You need to add **exactly**:
   ```
   http://localhost:8080/callback
   ```

**IMPORTANT:** Make sure it includes `/callback` at the end!

### Step 4: Save
1. Click the **SAVE** button (blue button at bottom)
2. Wait for confirmation

### Step 5: Clear Cache and Try Again
```bash
# Delete the cached token
rm config/google_tasks_token.pkl

# Try syncing again
python main.py sync
```

## Expected Behavior

When you run `python main.py sync`:

1. A browser window will open automatically
2. You'll see a Google sign-in page
3. Sign in with your Google account
4. Click "Allow" to grant access to Google Tasks
5. You'll see a message: "The authentication flow has completed"
6. The terminal will continue automatically and fetch your tasks

## Troubleshooting

### Still getting the error?
- Make sure you added `/callback` at the end
- Check for typos or extra spaces
- Try a fresh download of your credentials file

### Browser doesn't open?
- Check the terminal output for a URL
- Copy and paste that URL into your browser manually
- Complete the sign-in there

### Port 8080 is already in use?
- Close any other applications using port 8080
- Or restart your computer

### The app is using a different port (like 52391)?
- This means your credentials file may have the wrong redirect URI
- Go back to Google Cloud Console and check
- The redirect URI must be `http://localhost:8080/callback`


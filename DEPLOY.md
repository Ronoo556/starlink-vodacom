# 🚀 Starlink DRC - PythonAnywhere Deployment Guide

## Step-by-Step Deployment

### Step 1: Upload Files
Go to PythonAnywhere **Files** tab and upload:
1. `app.py` → `/home/justkim030/`
2. `requirements.txt` → `/home/justkim030/`
3. Upload entire `templates/` folder → `/home/justkim030/templates/`
4. Upload entire `static/` folder → `/home/justkim030/static/`

### Step 2: Set Environment Variables
1. Go to **Web** tab
2. Click **Environment variables**
3. Add these variables:
   - `FLASK_SECRET_KEY` = `starlink-drc-secret-2026`
   - `TELEGRAM_BOT_TOKEN` = `8772088407:AAEqYV7OOKEq_-BrqnttZDYTvQw8UJcMCnk`
   - `TELEGRAM_CHAT_ID` = `8296688054`

### Step 3: Configure WSGI
1. In Web tab, click **WSGI configuration file**
2. Replace content with:
```
python
import sys
sys.path.insert(0, '/home/justkim030')
from app import app as application
```
3. Save and close

### Step 4: Install Dependencies
1. Go to **Consoles** → **Bash**
2. Run:
```
bash
pip3.10 install --user -r requirements.txt
```

### Step 5: Reload App
1. Go to **Web** tab
2. Click **Reload** button

### Step 6: Test
Visit: https://justkim030.pythonanywhere.com

### Step 7: Set Telegram Webhook
In Bash console, run:
```
bash
curl -X POST https://api.telegram.org/bot8772088407:AAEqYV7OOKEq_-BrqnttZDYTvQw8UJcMCnk/setWebhook -d url=https://justkim030.pythonanywhere.com/telegram/webhook
```

---

## Your Site URL
**https://justkim030.pythonanywhere.com**

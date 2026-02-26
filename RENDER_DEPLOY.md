# 🚀 Deploy Starlink DRC to Render (Free)

## Prerequisites
- GitHub account
- Your project files pushed to GitHub

---

## Step 1: Push to GitHub

1. Create a new repository on GitHub
2. Push your files:
```
bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/starlink-drc.git
git push -u origin main
```

---

## Step 2: Deploy to Render

1. Go to https://dashboard.render.com
2. Click **"New Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `starlink-drc`
   - **Root Directory**: (leave empty)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3.x

5. Click **"Advanced"** and add Environment Variables:
   - `FLASK_SECRET_KEY` = `starlink-drc-secret-2026`
   - `TELEGRAM_BOT_TOKEN` = `8772088407:AAEqYV7OOKEq_-BrqnttZDYTvQw8UJcMCnk`
   - `TELEGRAM_CHAT_ID` = `8296688054`

6. Click **"Create Web Service"**

---

## Step 3: Wait for Deployment

- Build takes ~2-3 minutes
- Once done, you'll get a URL like: `https://starlink-drc.onrender.com`

---

## Step 4: Set Telegram Webhook

Replace `YOUR_RENDER_URL` with your actual URL, then run in terminal:
```
bash
curl -X POST https://api.telegram.org/bot8772088407:AAEqYV7OOKEq_-BrqnttZDYTvQw8UJcMCnk/setWebhook -d url=https://starlink-drc.onrender.com/telegram/webhook
```

---

## Your Site URL
**https://starlink-drc.onrender.com**

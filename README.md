# 🛰️ Starlink DRC Reseller — Full-Stack Web App

A complete Starlink internet reseller platform for the Democratic Republic of Congo (DRC) with Airtel Money payments and Telegram bot notifications.

---

## 🗂️ Project Structure

```
starlink-drc/
├── app.py                # Flask application (all routes + Telegram bot)
├── bot.py                # Standalone Telegram bot
├── schema.sql            # MySQL database schema + seed data
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── main.css              # Styles
├── main.js               # JavaScript
├── README.md             # This file
├── TELEGRAM_SETUP.md     # Telegram bot setup guide
└── templates/
    ├── index.html        # Plans / Home page
    ├── status.html       # Network Status page
    ├── orders.html       # Order Logs admin view
    ├── settings.html     # Settings page
    ├── payment.html      # Payment form
    ├── otp.html          # OTP verification
    ├── processing.html   # Processing overlay
    └── success.html      # Success page
```

---

## 🚀 Setup Guide

### 1. Clone & Install

```
bash
git clone <your-repo>
cd starlink-drc
pip install -r requirements.txt
```

### 2. MySQL Database

```
bash
# Create database and tables
mysql -u root -p < schema.sql
```

### 3. Environment Variables

```
bash
cp .env.example .env
# Edit .env with your values
nano .env
```

### 4. Update app.py Database URL

In `app.py`, update this line:
```
python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://USER:PASSWORD@localhost/starlink_drc'
```

### 5. Run Locally

```
bash
python app.py
# Visit: http://localhost:5000
```

---

## 📱 Telegram Bot Setup

### Step 1: Create Bot
1. Open Telegram → search `@BotFather`
2. Send `/newbot` → follow instructions
3. Copy the **bot token**

### Step 2: Get Chat ID
1. Add your bot to a group/channel
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Find `"chat":{"id": -100XXXXXXXXX}` — that's your **Chat ID**

### Step 3: Set Webhook
```
bash
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -d url=https://yourdomain.com/telegram/webhook
```

### Step 4: Update .env
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Bot Commands
| Command | Description |
|---------|-------------|
| `/start` | Show help menu |
| `/orders` | Last 5 orders |
| `/pending` | All pending orders |
| `/stats` | Network statistics |
| `/status` | System overview |
| `/complete SLR-00001` | Mark order as completed |

---

## 🌐 Deploy to PythonAnywhere

1. **Upload files** to PythonAnywhere
2. **Create MySQL database** in PythonAnywhere dashboard
3. **Import schema**:
   
```
bash
   mysql -u yourusername -p yourdatabase < schema.sql
   
```
4. **Install dependencies**:
   
```
bash
   pip3.10 install --user -r requirements.txt
   
```
5. **Configure WSGI** file:
   
```
python
   import sys
   sys.path.insert(0, '/home/yourusername/starlink-drc')
   from app import app as application
   
```
6. **Set environment variables** in PythonAnywhere → "Web" → "Environment variables":
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `DATABASE_URL` (your MySQL connection string)

---

## 🔌 Routes & Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | index.html | Plans / Home page |
| `/status` | status.html | Network Status |
| `/orders` | orders.html | Order Logs |
| `/settings` | settings.html | Settings |
| `/payment` | payment.html | Payment form |
| `/otp` | otp.html | OTP Verification |
| `/processing` | processing.html | Processing overlay |
| `/success` | success.html | Success page |

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/plans` | JSON list of plans |
| GET | `/api/orders` | JSON list of orders (paginated) |
| POST | `/api/orders` | Create new order |
| PATCH | `/api/orders/<id>` | Update order status/Airtel details |
| POST | `/api/orders/<id>/resend-otp` | Resend OTP (5-min cooldown) |
| GET | `/api/network-status` | Current network stats |
| POST | `/api/network-status` | Update network stats |
| POST | `/telegram/webhook` | Telegram bot webhook |

---

## 📊 Database Tables

- **plans** — Internet packages (name, data_gb, price_cdf)
- **customers** — Customer phone numbers
- **orders** — Order records with Airtel payment details
- **network_status** — Live download/upload/ping/jitter stats

---

## 💳 Order Statuses

| Status | Description |
|--------|-------------|
| `Pending` | Order created, awaiting payment |
| `Pin_Verified` | PIN entered, awaiting OTPs |
| `Completed` | Payment confirmed, service activated |
| `Failed` | Payment failed |

---

## 🔒 Security Notes

- Add authentication before deploying to production
- Use HTTPS (PythonAnywhere provides this free)
- Store secrets in environment variables, never in code
- Consider rate limiting the `/api/orders` endpoint

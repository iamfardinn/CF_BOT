# 🏆 Codeforces Contest Discord Bot

A production-ready Discord bot that automatically notifies your server about upcoming and ongoing Codeforces contests.

---

## ✨ Features

| Feature | Detail |
|---|---|
| ⏰ 1-Hour Warning | Sends a rich embed 1 hour before a contest begins |
| 🚀 Contest Started | Fires immediately when a contest goes live |
| 🔴 Ongoing Detection | Catches contests already running |
| 🎨 Division Colours | Unique colour per division (Div. 1, 2, 3, 4, Educational, Global Round) |
| 🔕 No Duplicates | `data/state.json` tracks sent notifications across restarts |
| 🌍 Auto Timezones | Uses Discord's `<t:UNIX:F>` timestamps — every user sees their local time |
| 📌 Slash Commands | `/next_contest`, `/ongoing`, `/help_cf` |
| 🔔 Role Mentions | Optional per-division role pings via `.env` |

---

## 📁 Project Structure

```
codeforces_bot/
├── bot.py                      # Entry point
├── config.py                   # Loads & validates .env
├── requirements.txt
├── .env.example                # Copy → .env and fill in
├── .gitignore
│
├── cogs/
│   ├── codeforces_monitor.py   # Background polling loop
│   └── slash_commands.py       # /next_contest, /ongoing, /help_cf
│
├── utils/
│   ├── cf_api.py               # Async Codeforces API client
│   ├── helpers.py              # Division detection, embeds, formatting
│   └── store.py                # state.json read/write (no duplicate pings)
│
└── data/
    └── state.json              # Auto-generated, tracks sent notifications
```

---

## 🚀 Quick Start

### Step 1 — Create a Discord Bot Application

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** → give it a name (e.g. `CF Contest Bot`)
3. Go to **Bot** → click **Reset Token** → copy the token
4. Under **Privileged Gateway Intents**, turn off everything (we don't need them)
5. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Embed Links`, `View Channels`
6. Open the generated URL in your browser and invite the bot to your server

### Step 2 — Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
DISCORD_TOKEN=your_bot_token_here
NOTIFICATION_CHANNEL_ID=123456789012345678
```

**How to get the Channel ID:**
- Enable Developer Mode in Discord: *User Settings → Advanced → Developer Mode*
- Right-click your notifications channel → **Copy ID**

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run the Bot

```bash
python bot.py
```

You should see:
```
2026-04-25 18:00:00  INFO      bot  Logged in as CF Contest Bot#1234 (ID: ...)
2026-04-25 18:00:00  INFO      bot  Synced 3 slash command(s) globally.
2026-04-25 18:00:00  INFO      ...  Contest monitor ready. Polling every 10 min...
```

> **Note:** Slash commands can take up to **1 hour** to appear globally on first launch. To test immediately, use guild-scoped sync (see `bot.py` comments).

---

## ⚙️ Configuration Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_TOKEN` | ✅ | — | Your bot token |
| `NOTIFICATION_CHANNEL_ID` | ✅ | — | Channel to post notifications |
| `NOTIFY_BEFORE_MINUTES` | ❌ | `60` | Minutes before contest to warn |
| `POLL_INTERVAL_MINUTES` | ❌ | `10` | How often to poll the CF API |
| `ROLE_DIV1` | ❌ | — | Role ID to ping for Div. 1 |
| `ROLE_DIV2` | ❌ | — | Role ID to ping for Div. 2 |
| `ROLE_DIV3` | ❌ | — | Role ID to ping for Div. 3 |
| `ROLE_DIV4` | ❌ | — | Role ID to ping for Div. 4 |
| `ROLE_EDUCATIONAL` | ❌ | — | Role ID to ping for Educational |
| `ROLE_GLOBAL` | ❌ | — | Role ID to ping for Global Rounds |
| `ROLE_OTHER` | ❌ | — | Role ID for all other contests |

---

## 📋 Slash Commands

| Command | Options | Description |
|---|---|---|
| `/next_contest` | `division`, `count` | Show upcoming contests, filtered optionally |
| `/ongoing` | — | Show all live contests right now |
| `/help_cf` | — | Bot info and command list |

---

## 🛡️ Edge Cases Handled

| Scenario | How It's Handled |
|---|---|
| API down / timeout | 3 retries with exponential back-off (2s, 4s, 8s) |
| Bot restarted mid-contest | `state.json` remembers sent notifications |
| Contest phase lag (CF API slow) | Extra logic catches contests that should be `CODING` but still show `BEFORE` |
| Duplicate pings | `already_notified()` check before every send |
| Old contest IDs accumulating | `prune_old_entries()` cleans `state.json` each poll cycle |
| Timezone confusion | Discord timestamps `<t:UNIX:F>` auto-convert for each viewer |

---

## ☁️ Deployment

### Local (always-on)

Keep the terminal open, or use a process manager:
```bash
# Windows — run as a background service with NSSM
# https://nssm.cc/

nssm install CodeforcesBot python a:\Devops_Thesis\codeforces_bot\bot.py
nssm start CodeforcesBot
```

### VPS / Linux Server

```bash
# Install deps in a venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run with systemd or screen
screen -S cfbot python bot.py
```

### Render.com (Free PaaS)

1. Push this folder to a GitHub repository
2. Create a new **Background Worker** on [render.com](https://render.com)
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `python bot.py`
5. Add your `.env` values as Environment Variables in the Render dashboard

---

## 🤝 Contributing

Pull requests are welcome! The cog-based architecture makes it easy to add new features without touching existing code.

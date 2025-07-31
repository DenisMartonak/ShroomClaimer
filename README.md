# 🍄 ShroomClaimer

**ShroomClaimer** is an automated Python bot that logs into a website, claims a virtual gift (referred to as a "shroom"), and sends the result to a Discord webhook for notification. It is intended to be run on a scheduled basis, for example via [Make.com](https://make.com), to automate the gift-claiming process.

---

## 📚 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Example](#example)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Features

- Logs in to a website using provided credentials
- Sends a POST request to claim a gift
- Sends a rich Discord embed via webhook indicating success or failure
- Auto re-authenticates on unauthorized response
- Designed for automation via Make.com or similar schedulers

---

## 🛠️ Installation

```bash
git clone https://github.com/DenisMartonak/ShroomClaimer.git
cd ShroomClaimer
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a `.env` file in the project root with the following environment variables:

```env
USERNAME=your_username
PASSWORD=your_password
LOGIN_URL=https://example.com/login
CLAIM_URL=https://example.com/claim
WEBHOOK_URL=https://discord.com/api/webhooks/...
```

> 🔒 Keep your `.env` file secure. Never share it publicly.

---

## ▶️ Usage

You can run the bot manually from the command line:

```bash
python bot.py
```

This will:

1. Log in to the website using credentials from `.env`
2. Attempt to claim a gift
3. Post the result to your specified Discord webhook

---

## 🧪 Example Discord Output

On success:
> **Shroom bot response ✅**  
> Status: `success`  
> Message: `Hourly gift claimed successfully`

On failure:
> **Shroom bot response ❌**  
> Status: `error`  
> Message: `You already claimed this gift`

---

## 📦 Dependencies

- `requests` - for HTTP requests
- `python-dotenv` - for environment variable loading
- `aiohttp` - for async HTTP handling
- `discord` - for Discord webhook embeds

Install them with:

```bash
pip install -r requirements.txt
```

---

## 🧯 Troubleshooting

- **Login failed**: Double-check your `USERNAME`, `PASSWORD`, and `LOGIN_URL`.
- **Unauthorized**: The script will retry login automatically. Ensure credentials are valid.
- **Webhook failed**: Confirm the `WEBHOOK_URL` is correct and the bot has permission to post.
- **GIF not showing**: Discord may block certain GIFs; use static images if needed.

---

## 📄 License

This project is not currently licensed.

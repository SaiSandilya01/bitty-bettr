# BittyBettr

**BittyBettr** is a minimalist, local-first engine that captures your random sparks of curiosity—about history, science, technology, or philosophy—and transforms them into a beautifully crafted, in-depth **Daily Learning Digest** sent directly to your Kindle.

Built with Python, FastAPI, and powered by Google Gemini (or OpenAI), BittyBettr skips the databases and complex infrastructure in favor of a clean, hacker-friendly local MVP.

---

## 🚀 Features

- **Topic Capture API**: A lightweight FastAPI server to instantly POST any topic you want to learn about.
- **Deduplication Engine**: Uses a simple, flat-file storage system (`topics.txt`) to ensure you never learn the same thing twice.
- **Deep-Dive LLM Generation**: Instructs the LLM to write like a long-form New Yorker profile—breaking down intuition, history, deep mechanics, and real-world examples.
- **Direct-to-Kindle Delivery**: Automatically bundles your daily digest into clean, Kindle-native HTML and emails it straight to your device via SMTP.
- **Multi-Provider LLM Support**: Designed out-of-the-box to effortlessly swap between Google Gemini and OpenAI with a single `.env` variable.

---

## 🛠 Prerequisites

- Python 3.9+
- A Google Gemini API Key (Free tier works perfectly) or OpenAI API Key.
- A Kindle device (or Kindle app) configured to receive documents via email.

---

## 📦 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SaiSandilya01/bitty-bettr.git
   cd bitty-bettr
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure your environment:**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and configure:
   - Your LLM Provider and API Key (`GEMINI_API_KEY`)
   - Your target Kindle email address (`KINDLE_EMAIL`)
   - Your SMTP credentials (`SMTP_USER`, `SMTP_PASSWORD`) 
   *(Note: For Gmail, you MUST generate an App Password in your Google Account Security settings).*

4. **Whitelist your Email with Amazon:**
   Log into your Amazon Account → Manage Your Content and Devices → Preferences → Personal Document Settings. Ensure your `SMTP_USER` email is on the **Approved Personal Document E-mail List**.

---

## 📖 Usage

### Step 1: Start the API Server
Leave this running in the background to capture your thoughts throughout the day.
```bash
source .venv/bin/activate
uvicorn main:app --reload
```

### Step 2: Queue Up Topics
Whenever you encounter something you want a deep dive into, hit the API:
```bash
curl -X POST http://localhost:8000/topics \
     -H "Content-Type: application/json" \
     -d '{"topic": "Compound Interest"}'

curl -X POST http://localhost:8000/topics \
     -H "Content-Type: application/json" \
     -d '{"topic": "Stoicism"}'
```

### Step 3: Generate & Send Your Digest
At the end of your day (or via a morning Cron job), run the generator:
```bash
python3 digest_runner.py
```
The engine will read your queued topics, orchestrate the LLM deep-dives, generate a single self-contained HTML document (`digest.html`), and instantly email it to your Kindle for reading!

---

## 🏛 Architecture

- **`main.py` & `routers/`**: The FastAPI application serving REST endpoints.
- **`storage/topic_store.py`**: The file I/O layer isolating the flat-file DB from the rest of the app.
- **`llm/`**: The Abstract LLM Factory, implementing the provider clients and housing the structured prompt template.
- **`services/email_service.py`**: Manages the TLS SMTP handshake and constructs multipart attachments for Amazon.
- **`digest_runner.py`**: The stateless CLI entry point that orchestrates the run cycle.

---

## 📱 Telegram Bot

Queue topics and trigger digest generation directly from your phone — no curl commands needed.

### Setup

1. **Create a bot** via [@BotFather](https://t.me/botfather) on Telegram and copy the token.
2. **Add the token** to your `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
   ```
3. **Install the dependency** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the bot** (in a separate terminal from the API server):
   ```bash
   source .venv/bin/activate
   python -m telegram_bot.bot
   ```

### Commands

| Command | Description |
|---|---|
| `/start` | Welcome message & command list |
| `/add <topic>` | Add a topic to the queue |
| `/list` | Show all queued topics |
| `/clear` | Remove all queued topics |
| `/digest` | Generate the digest and email it to your Kindle |

> **Tip:** The bot and FastAPI server share the same `topics.txt` file, so you can mix-and-match — add topics via the API and send the digest via Telegram, or vice versa.

---

## 🤝 Next Steps / Expansion Features
- [x] Connect a Telegram Bot to `topics.txt` so you can text ideas to your queue from your phone.
- [ ] Setup a strictly scheduled crontab daemon to fully automate generation at 7:00 AM.
- [ ] Add EPUB native conversion using `ebooklib` for complex embedded images.

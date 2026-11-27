# Matlade Phone (మాట్లాడే ఫోన్)

Matlade Phone is an end-to-end prototype built for Round 2 of the Wispr x Scaler **"India Runs on Voice"** hackathon. It converts English SMS alerts—such as bank debits, credits/salary alerts, bill reminders, and OTP messages—into structured Telugu text and spoken Telugu voice readouts.

The prototype runs locally using a deterministic, rule-based Telugu SMS parser and requires **zero secret API keys** to start and test.

---

## Key Features

- **Local Rule-Based Telugu SMS Parser (`sms_translator.py`):** Categorizes incoming SMS alerts (`debit`, `credit`, `bill`, `otp`, or `general`) and extracts key details such as amounts, balances, masked account numbers, dates, and OTP codes using regular expressions.
- **Natural Telugu Output:** Formats extracted details into clear Telugu sentences so users can read or listen to what happened without deciphering English banking shorthand.
- **Browser Voice Readout (`static/app.js`):** Uses the Web Speech API (`speechSynthesis` with `te-IN` language preference) to read converted Telugu messages aloud, with controls to stop playback and graceful fallback notices when a Telugu TTS voice is unavailable on a device.
- **Zero Secret Keys Required:** Works out of the box with no mandatory API keys or external cloud dependencies. An optional `OPTIONAL_CLOUD_KEY` environment variable is supported in `docker-compose.yml` for configuration awareness while keeping the local offline parser active.
- **Session Readout History:** Keeps a lightweight in-memory log of recent conversions during the active session (`GET /api/history` and `POST /api/translate`), plus a health check endpoint (`GET /api/health`).

---

## Repository Structure

```text
matlade-phone/
├── app.py               # Flask web server and REST endpoints (/, /api/health, /api/translate, /api/history)
├── sms_translator.py    # Sample SMS alerts, regex entity extractors, and Telugu message builder
├── requirements.txt     # Python dependencies (Flask)
├── Dockerfile           # Container build definition (python:3.11-slim)
├── docker-compose.yml   # Single-command service and port 5000 configuration
├── templates/
│   └── index.html       # Web UI for sample/custom SMS input, Telugu output, and voice controls
└── static/
    └── app.js           # Client-side API calls, session history rendering, and speech synthesis
```

---

## Running Locally with Docker Compose

### Prerequisites

- Docker Desktop installed and running (with WSL2 backend enabled on Windows).

### Steps

1. Clone or download this repository and open a terminal in the project root folder:

   ```bash
   git clone https://github.com/julurijanu-pixel/matlade-phone.git
   cd matlade-phone
   ```

2. Build and start the container:

   ```bash
   docker compose up --build
   ```

3. Open your browser and go to:

   ```text
   http://localhost:5000
   ```

4. Click any sample alert button (`Bank Debit Alert`, `Salary / Credit Alert`, `Electricity Bill Reminder`, `Security OTP Alert`) or paste your own English SMS, click **Convert to Telugu**, and use **Read Aloud (Telugu Voice)** / **Stop Voice** to test audio readout.

---

## Architecture & Fallback Notes

- **Deterministic Local Parsing:** Because financial and utility SMS alerts follow structured templates and abbreviations (such as `Acct`, `Avl Bal`, `INR`, `Rs.`, and `NEFT`), rule-based extraction provides predictable latency, offline reliability, and zero per-request API cost.
- **Voice Readout Fallback:** Spoken playback relies on the user's browser and operating system speech synthesis support for `te-IN`. If no Telugu voice pack is installed on the host machine, the UI still displays the full Telugu text readout and reports the fallback status clearly.
- **Prototype Scope:** Session history is stored in memory while the container is running and resets when the container restarts. No real SMS inbox access, banking credentials, or secret API keys are stored in this repository.
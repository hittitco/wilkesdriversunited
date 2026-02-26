# WilkesDriversUnited bot (prototype)

This folder contains a minimal prototype of the Discord bot + FastAPI server used to provide the public `/status` endpoint for the landing page.

Files
- `main.py` - FastAPI app + simple Discord client. Hosts GET `/status` and POST `/reset` and listens for plain-text `/clockin` and `/clockout` commands in Discord.
- `requirements.txt` - Python dependencies.

Environment
- `DISCORD_TOKEN` (required to start the bot)
- `ADMIN_TOKEN` (optional) - if set, must be provided in header `X-Admin-Token` to `POST /reset`.
- `ADMIN_IDS` (optional) - comma-separated Discord user IDs that count as admins for in-bot checks (not used in this prototype).
- `PORT` (optional) - port for FastAPI (default 8000)
- `AUTO_TIMEOUT_SECONDS` (optional) - number of seconds before a user is auto-removed (default 4 hours)

Run locally (recommended via virtualenv)

1. Create virtual environment and install deps:

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r bot\requirements.txt

2. Create a small `.env` or export env vars in your shell. Example `.env`:

   DISCORD_TOKEN=your_bot_token_here
   ADMIN_TOKEN=some-secret-token
   PORT=8000

3. Run the bot (development):

   python bot\main.py

Notes and next steps
- This prototype uses an in-memory store and is intended for v1 only. For production, consider persistent storage (Redis), graceful shutdown, and secure CORS/origins.
- The landing page should poll `GET /status` every ~10-30s to update the floating widget. Use the `online` field in the response.

Railway deployment (quick guide)

You can deploy this bot to Railway. Keep in mind Railway either uses a Procfile at the repo root or you can set custom build/start commands in the project settings. Since you asked to keep files inside the `bot/` folder, this README describes two simple options.

Option A — use a custom Build & Start command (recommended if you keep `Procfile` inside `bot/`):

1. In Railway project settings set the Build command to:

   pip install -r bot/requirements.txt

2. Set the Start command to (Railway will provide $PORT automatically):

   python bot/main.py

3. Add environment variables in Railway (use values from `bot/.env.example`). Be sure to set `DISCORD_TOKEN` and optionally `ADMIN_TOKEN`.

Option B — Procfile method

- A `bot/Procfile` is included that runs `python bot/main.py` but Railway expects `Procfile` at the repository root. If you prefer the Procfile approach, either move `bot/Procfile` to the repo root or set the Start command to `python bot/main.py` in Railway instead of relying on Procfile auto-detection.

Environment variables
- Use the `bot/.env.example` file as a checklist for required variables. Set at minimum `DISCORD_TOKEN` in Railway. Optionally set `ADMIN_TOKEN` and `ADMIN_IDS` to control admin resets.

Notes and tips
- Build step must install dependencies from `bot/requirements.txt` because the requirements file lives inside `bot/`.
- Railway will provide a `PORT` variable — the bot reads `PORT` and uses it for the FastAPI server.
- For production consider using Redis (managed) for state persistence; you can add a managed Redis plugin in Railway and update `main.py` to use it.


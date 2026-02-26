# CO-PILOT CONTEXT: WilkesDriversUnited (WDU)

## 🎯 Project Mission
A private community platform for Spark Drivers in Wilkesboro, NC. 
Focus: Support, strategy, and live driver coordination.

## 🛠️ Technical Constraints (STRICT)
- **Architecture:** Single-file HTML/CSS/JS (`index.html`).
- **Frameworks:** ZERO. Vanilla JS only. No React/Vue/Tailwind.
- **Styling:** "Cipher Nebula" Theme. 
  - BG: #050410 (Dark Void)
  - Primary: #6366f1 (Indigo)
  - Secondary: #e11d48 (Crimson)
  - Accents: Fuchsia
- **Deployment:** GitHub Pages (hittitco.github.io/wilkesdriversunited).

## 🧩 Key Components & IDs
- **CB Radio:** `#cbFreq`, `#cbStatus`. JS function `cbRadio()` handles frequency scrolling.
- **Driver Status Widget:** `#driverPanel`, `#dpNum`, `#dpLabel`. 
- **Form:** Formspree ID `xbdawlzq`.
- **Bot Integration:** - `STATUS_API_URL` (currently null).
  - `REFRESH_INTERVAL` (300000ms demo, 30000ms live).
  - Logic: Discord `/clockin` updates a FastAPI endpoint.

## 🤖 Discord Structure (Reference)
- **Categories:** [INFO], [COMMUNITY], [cb-radio], [ADMIN], [OG LOUNGE], [THE GARAGE].
- **Bot Logic:** Python (discord.py + FastAPI). 
-
## AOU
🚦 Final Architecture (So You’re Confident)

Discord Users
→ /clockin, /ping, /clockout
→ Python bot updates in-memory dictionary

FastAPI Endpoint
→ GET /status
→ Returns:

{ "online": 3 }

Website Widget
→ Polls every 30 seconds
→ Updates:

#dpNum

#dpUpdated

Toggles .offline if count = 0

That’s clean.
## 📝 Guidelines for Copilot
1. NEVER suggest a "rebuild" or "refactor" into a framework.
2. Edit `index.html` directly.
3. Keep CSS inside `<style>` and JS inside `<script>` tags within the main file.
4. Always prioritize mobile-responsive design for drivers on the road.
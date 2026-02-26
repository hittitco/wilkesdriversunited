import os
import time
import asyncio
import logging
import os
import time
import asyncio
import logging
from typing import Dict

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

import discord
from discord import Intents, app_commands

from uvicorn import Config, Server

LOG = logging.getLogger("wdu-bot")
logging.basicConfig(level=logging.INFO)

# Shared in-memory store: { user_id: last_active_epoch }
active: Dict[int, float] = {}
lock = asyncio.Lock()

# Configuration from env
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")  # for POST /reset
ADMIN_IDS = set(int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip())
PORT = int(os.getenv("PORT", "8000"))

AUTO_TIMEOUT_SECONDS = int(os.getenv("AUTO_TIMEOUT_SECONDS", str(4 * 3600)))  # default 4 hours
PURGE_INTERVAL_SECONDS = int(os.getenv("PURGE_INTERVAL_SECONDS", str(30 * 60)))  # default 30min

app = FastAPI()

# Allow the site to poll this endpoint from any origin (update for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)


@app.get("/status")
async def get_status():
    """Public endpoint returning the live count of active drivers."""
    async with lock:
        count = len(active)
    return {"online": count}


@app.post("/reset")
async def post_reset(x_admin_token: str | None = Header(None)):
    """Admin-only reset (protected by ADMIN_TOKEN header X-Admin-Token).

    Provide header `X-Admin-Token: <ADMIN_TOKEN>` to authorize.
    """
    if not ADMIN_TOKEN:
        raise HTTPException(status_code=503, detail="Admin reset not configured")
    if not x_admin_token or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    async with lock:
        active.clear()
    return {"ok": True, "online": 0}


# Discord bot setup
intents = Intents.default()
bot = discord.Client(intents=intents)


async def purge_task():
    """Background task that removes users inactive for AUTO_TIMEOUT_SECONDS."""
    while True:
        await asyncio.sleep(PURGE_INTERVAL_SECONDS)
        now = time.time()
        removed = []
        async with lock:
            for uid, ts in list(active.items()):
                if now - ts > AUTO_TIMEOUT_SECONDS:
                    removed.append(uid)
                    active.pop(uid, None)
        if removed:
            LOG.info("Auto-removed %d users for inactivity", len(removed))


@bot.event
async def on_ready():
    LOG.info("Discord client ready as %s", bot.user)
    # Start purge background task
    bot.loop.create_task(purge_task())
    # Sync application commands (slash commands)
    try:
        await bot.tree.sync()
        LOG.info("Synced application commands")
    except Exception as e:
        LOG.warning("Failed to sync app commands: %s", e)


async def start_uvicorn():
    config = Config(app=app, host="0.0.0.0", port=PORT, log_level="info")
    server = Server(config=config)
    await server.serve()


async def start_bot():
    if not DISCORD_TOKEN:
        LOG.warning("DISCORD_TOKEN not set; bot will not start")
        return
    await bot.start(DISCORD_TOKEN)


def _count_active() -> int:
    return len(active)


def is_admin_user(user: discord.User | discord.Member) -> bool:
    try:
        if hasattr(user, "guild_permissions") and getattr(user, "guild_permissions").administrator:
            return True
    except Exception:
        pass
    if user.id in ADMIN_IDS:
        return True
    return False


@bot.event
async def on_message(message: discord.Message):
    # Simple text commands fallback (in addition to slash commands)
    if message.author.bot:
        return
    content = message.content.strip().lower()
    if content == "/clockin":
        async with lock:
            active[message.author.id] = time.time()
            count = _count_active()
        await message.channel.send(f"✅ {message.author.display_name} clocked in. {count} drivers online.")
    elif content == "/clockout":
        async with lock:
            active.pop(message.author.id, None)
            count = _count_active()
        await message.channel.send(f"👋 {message.author.display_name} clocked out. {count} drivers online.")
    elif content == "/drivers":
        async with lock:
            count = _count_active()
        await message.channel.send(f"🚦 Drivers online: {count}")


# Slash commands
@bot.tree.command(name="clockin", description="Mark yourself as clocked in (driver online)")
async def sc_clockin(interaction: discord.Interaction):
    async with lock:
        active[interaction.user.id] = time.time()
        count = _count_active()
    await interaction.response.send_message(f"✅ You're clocked in. {count} drivers online.")


@bot.tree.command(name="clockout", description="Mark yourself as clocked out (driver offline)")
async def sc_clockout(interaction: discord.Interaction):
    async with lock:
        active.pop(interaction.user.id, None)
        count = _count_active()
    await interaction.response.send_message(f"👋 Clocked out. {count} drivers still online.")


@bot.tree.command(name="drivers", description="Show current count of online drivers")
async def sc_drivers(interaction: discord.Interaction):
    async with lock:
        count = _count_active()
    await interaction.response.send_message(f"🚦 Drivers online: {count}")


@bot.tree.command(name="reset", description="(Admin) Reset all counts")
async def sc_reset(interaction: discord.Interaction):
    if not is_admin_user(interaction.user):
        await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
        return
    async with lock:
        active.clear()
    await interaction.response.send_message("✅ Reset complete. 0 drivers online.")


async def main():
    # Run both uvicorn and discord bot concurrently
    await asyncio.gather(start_uvicorn(), start_bot())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOG.info("Shutting down")

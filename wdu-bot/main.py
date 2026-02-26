import os
import time
from dotenv import load_dotenv
from discord.ext import commands
from fastapi import FastAPI
import uvicorn

# load configuration from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 8000))

# discord bot setup
bot = commands.Bot(command_prefix="/")

# simple in-memory store of clocked-in users and last ping timestamp
active_users = {}  # user_id -> last_timestamp

@bot.command()
async def clockin(ctx):
    active_users[ctx.author.id] = time.time()
    await ctx.send("✅ You are now clocked in.")

@bot.command()
async def ping(ctx):
    if ctx.author.id in active_users:
        active_users[ctx.author.id] = time.time()
        await ctx.send("🔄 Your status has been refreshed.")
    else:
        await ctx.send("❌ You are not clocked in. Use `/clockin` first.")

@bot.command()
async def clockout(ctx):
    if ctx.author.id in active_users:
        del active_users[ctx.author.id]
        await ctx.send("👋 You have been clocked out.")
    else:
        await ctx.send("❌ You're not clocked in.")

# background task to purge stale entries
async def purge_task():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = time.time()
        cutoff = now - 45 * 60  # 45 minutes
        to_remove = [uid for uid, ts in active_users.items() if ts < cutoff]
        for uid in to_remove:
            del active_users[uid]
        await asyncio.sleep(60)

bot.loop.create_task(purge_task())

# fastapi web server exposing simple status endpoint
app = FastAPI()

@app.get("/status")
def status():
    # count users who have been pinged within last 45 minutes
    now = time.time()
    cutoff = now - 45 * 60
    count = sum(1 for ts in active_users.values() if ts >= cutoff)
    return {"drivers_online": count}


if __name__ == "__main__":
    # run both bot and web app on same event loop
    bot.loop.create_task(bot.start(TOKEN))
    uvicorn.run(app, host="0.0.0.0", port=PORT)

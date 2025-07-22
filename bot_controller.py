import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

# Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Load commands
import commands.ping
commands.ping.setup(bot)
import commands.sheet
commands.sheet.setup(bot)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await bot.tree.sync()

# Run the bot
bot.run(TOKEN)
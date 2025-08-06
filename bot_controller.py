import commands.sheet
import commands.ping
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

print("Loading commands...")
commands.ping.setup(bot)
print("✅ Loaded ping commands")

commands.sheet.setup(bot)
print("✅ Loaded sheet commands")


@bot.event
async def on_ready():
    """
    Event handler for when the bot is ready and connected to Discord.
    Displays bot information, guild details, and permission status.
    """
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Using Spreadsheet ID: {SPREADSHEET_ID}')

    if bot.guilds:
        print(f"Bot is in {len(bot.guilds)} guild(s):")
        for guild in bot.guilds:
            print(f"  - {guild.name} (ID: {guild.id})")
            bot_member = guild.get_member(bot.user.id)
            if bot_member:
                print(f"    Permissions: {bot_member.guild_permissions}")
    else:
        print("❌ Bot is not in any guilds!")


@bot.event
async def on_command_error(ctx, error):
    """
    Event handler for command errors.
    Logs command errors to console.
    """
    print(f"Command error: {error}")


@bot.event
async def on_app_command_error(interaction, error):
    """
    Event handler for slash command errors.
    Logs errors and sends error message to user.
    """
    print(f"Slash command error: {error}")
    try:
        await interaction.response.send_message(f"❌ Error: {str(error)}", ephemeral=True)
    except:
        pass

bot.run(TOKEN)

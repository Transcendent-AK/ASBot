import discord

def setup(bot):
    @bot.tree.command(name="ping", description="Sends the bot's latency.")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! Latency is {round(bot.latency * 1000)}ms")
    
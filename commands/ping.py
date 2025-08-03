import discord

def setup(bot):
    """
    Setup function for ping command.
    Registers the ping slash command with the bot.
    
    Args:
        bot: The Discord bot instance
    """
    @bot.tree.command(name="ping", description="Sends the bot's latency.")
    async def ping(interaction: discord.Interaction):
        """
        Slash command to check bot latency.
        Responds with the bot's current latency in milliseconds.
        
        Args:
            interaction: The Discord interaction object
        """
        await interaction.response.send_message(f"Pong! Latency is {round(bot.latency * 1000)}ms")
    
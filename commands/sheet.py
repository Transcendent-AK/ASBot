import discord

def setup(bot):
    @bot.tree.command(name="sheet_action", description="Select your sheet action")
    async def sheet_action(interaction: discord.Interaction):
        class ActionView(discord.ui.View):
            @discord.ui.button(label="Add", style=discord.ButtonStyle.success, custom_id="add_button")
            async def add_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                await interaction.response.send_message("You chose to add!", ephemeral=True)
                # Here you can trigger your add modal or logic

            @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger, custom_id="remove_button")
            async def remove_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                await interaction.response.send_message("You chose to remove!", ephemeral=True)
                # Here you can trigger your remove modal or logic

            @discord.ui.button(label="Edit", style=discord.ButtonStyle.secondary, custom_id="edit_button")
            async def edit_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                await interaction.response.send_message("You chose to edit!", ephemeral=True)
                # Here you can trigger your edit modal or logic

        await interaction.response.send_message(
            "Select your action:",
            view=ActionView(),
            ephemeral=True
        )
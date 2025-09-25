import discord
import re
from datetime import datetime, timedelta
from utils.masterlist_ops import add_player_to_guild, remove_player_from_guild, edit_player_in_guild, find_player
from utils.watchlist_ops import add_player_to_banlist, remove_player_from_banlist, edit_player_in_banlist
from utils.google_sheet import get_sheet
import os
from dotenv import load_dotenv

load_dotenv()
multi_modal_store = {}

class PersistentActionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout - persistent

    @discord.ui.button(label="Add Player to Masterlist", style=discord.ButtonStyle.green, custom_id="persistent_add")
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Create a view with the status select menu
            view = discord.ui.View()
            view.add_item(StatusSelect())
            await interaction.response.send_message(
                "Select player status:",
                view=view,
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error opening select menu: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Remove Player from Masterlist", style=discord.ButtonStyle.red, custom_id="persistent_remove")
    async def remove_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(RemovePlayerModal())
        except Exception as e:
            await interaction.followup.send(f"❌ Error opening modal: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Edit Player in Masterlist", style=discord.ButtonStyle.gray, custom_id="persistent_edit")
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(EditPlayerModal())
        except Exception as e:
            await interaction.followup.send(f"❌ Error opening modal: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Add Player in Watchlist", style=discord.ButtonStyle.red, custom_id="persistent_watchlist")
    async def watchlist_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            view = discord.ui.View()
            view.add_item(BanStatus())
            await interaction.response.send_message(
                "Select player punishment reason:",
                view=view,
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error opening menu: {str(e)}", ephemeral=True)


class RemovePlayerModal(discord.ui.Modal, title="Remove Player from Masterlist"):
    player_id = discord.ui.TextInput(
        label="Player IGN to Remove",
        placeholder="Enter the player IGN to remove from the Masterlist",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            success, message = remove_player_from_guild(self.player_id.value, interaction.user.name)
            await interaction.followup.send(message, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

class EditPlayerModal(discord.ui.Modal, title="Edit Player in Masterlist - Step 1"):
    player_ign = discord.ui.TextInput(
        label="Player IGN to Edit",
        placeholder="Enter the player IGN to edit",
        required=True,
        max_length=50
    )
    discord_id = discord.ui.TextInput(
        label="Discord ID",
        placeholder="Enter Discord ID (e.g., 551475914809786890)",
        required=False,
        max_length=20
    )
    known_alts = discord.ui.TextInput(
        label="Known Alts",
        placeholder="Enter known alternate accounts (separate with commas)",
        required=False,
        max_length=200
    )
    house = discord.ui.TextInput(
        label="House",
        placeholder="Enter house name",
        required=False,
        max_length=50
    )
    notes = discord.ui.TextInput(
        label="Notes",
        placeholder="Enter any additional notes",
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            multi_modal_store[interaction.user.id] = {
                "player_ign": self.player_ign.value,
                "discord_id": self.discord_id.value or "",
                "known_alts": self.known_alts.value or "",
                "house": self.house.value or "",
                "notes": self.notes.value or "",
            }
            await interaction.response.send_message(
            "✅ Step 1 complete! Click below to continue to Step 2.",
            view=ContinueToStep2EditView(),
            ephemeral=True
        )
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class EditPlayerModalStep2(discord.ui.Modal):
    def __init__(self, player_ign, rank, status, discord_id, known_alts):
        super().__init__(title="Edit Player in Masterlist - Step 2")

        # Save values for later use in on_submit
        self.player_ign = player_ign
        self.rank = rank
        self.status = status
        self.discord_id = discord_id
        self.known_alts = known_alts

        # Define and add the input field
        self.sus_alert = discord.ui.TextInput(
            label="Suspicious Alert (Optional)",
            placeholder="Enter 'Yes' or 'No' for suspicious alert - Leave empty for No",
            required=False,
            max_length=3
        )

        self.add_item(self.sus_alert)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            data = multi_modal_store.pop(interaction.user.id, {})
            action_by_value = data.get('action_by', '')
            sus_alert_value = self.sus_alert.value.strip().lower() if self.sus_alert.value else "no"

            if sus_alert_value not in ['yes', 'no']:
                await interaction.followup.send("❌ Suspicious Alert must be 'Yes' or 'No'", ephemeral=True)
                return

            sus_alert_boolean = sus_alert_value == "yes"
            current_row = find_player(self.player_ign)
            if not current_row:
                await interaction.followup.send("❌ Player not found in Masterlist.", ephemeral=True)
                return

            row_data = [
                self.player_ign,
                current_row[1],  # Join Date
                current_row[2],  # Rank
                current_row[3],  # Status
                self.known_alts or current_row[4],
                data.get("house", current_row[5]),
                self.discord_id or current_row[6],
                data.get("notes", current_row[7]),
                sus_alert_boolean,
            ]

            success, message = edit_player_in_guild(self.player_ign, row_data, action_by_value)
            await interaction.followup.send(message, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

class CustomEditDateModal(discord.ui.Modal, title="Enter Custom Date"):
    custom_date = discord.ui.TextInput(
        label="Custom Date",
        placeholder="Enter date in MM/DD/YYYY format (e.g., 12/15/2024)",
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validate date format
            date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
            if not re.match(date_pattern, self.custom_date.value):
                await interaction.response.send_message("❌ Invalid date format. Please use MM/DD/YYYY", ephemeral=True)
                return
            
            # Store the custom date and show the edit modal
            await interaction.response.send_modal(EditPlayerModalWithDate(self.custom_date.value))
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class CustomDateModal(discord.ui.Modal, title="Enter Custom Date"):
    def __init__(self, selected_status: str):
        super().__init__()
        self.selected_status = selected_status

    custom_date = discord.ui.TextInput(
        label="Custom Date",
        placeholder="Enter date in MM/DD/YYYY format (e.g., 12/15/2024)",
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
            if not re.match(date_pattern, self.custom_date.value):
                await interaction.response.send_message("❌ Invalid date format. Please use MM/DD/YYYY", ephemeral=True)
                return
            
            await interaction.response.edit_message(
                content="Select player rank:",
                view=RankSelectView(self.selected_status, self.custom_date.value)
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class AddPlayerModalWithDate(discord.ui.Modal, title="Add Player to Masterlist - Step 1"):
    def __init__(self, selected_date: str, selected_status: str, selected_rank: str):
        super().__init__()
        self.selected_date = selected_date
        self.selected_status = selected_status
        self.selected_rank = selected_rank

    player_ign = discord.ui.TextInput(
        label="IGN (In-Game Name)",
        placeholder="Enter the player's in-game name (e.g., John Doe)",
        required=True,
        max_length=50
    )
    discord_id = discord.ui.TextInput(
        label="Discord ID",
        placeholder="Enter Discord ID (e.g., 551475914809786890)",
        required=False,
        max_length=20
    )
    known_alts = discord.ui.TextInput(
        label="Known Alts",
        placeholder="Enter known alternate accounts (separate with commas)",
        required=False,
        max_length=200
    )
    house = discord.ui.TextInput(
        label="House",
        placeholder="Enter house name",
        required=False,
        max_length=50
    )
    notes = discord.ui.TextInput(
        label="Notes",
        placeholder="Enter any additional notes",
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            multi_modal_store[interaction.user.id] = {
                "player_ign": self.player_ign.value,
                "discord_id": self.discord_id.value or "",
                "known_alts": self.known_alts.value or "",
                "house": self.house.value or "",
                "notes": self.notes.value or "",
                "selected_date": self.selected_date,
                "selected_status": self.selected_status,
                "selected_rank": self.selected_rank,
            }
            await interaction.response.send_message(
                "Click below to continue..",
                view=ContinueToStep2View(),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class AddPlayerModalStep2(discord.ui.Modal, title="Add Player to Masterlist - Step 2"):
    def __init__(self, selected_date: str, selected_status: str, selected_rank: str, 
                 player_ign: str, discord_id: str, known_alts: str, house: str, notes: str):
        super().__init__()
        self.selected_date = selected_date
        self.selected_status = selected_status
        self.selected_rank = selected_rank
        self.player_ign = player_ign
        self.discord_id = discord_id
        self.known_alts = known_alts
        self.house = house
        self.notes = notes

    sus_alert = discord.ui.TextInput(
        label="Suspicious Alert (Optional)",
        placeholder="Enter 'Yes' or 'No' for suspicious alert - Leave empty for No",
        required=False,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            data = multi_modal_store.pop(interaction.user.id, {})
            sus_alert_value = self.sus_alert.value.strip().lower() if self.sus_alert.value else "no"
            if sus_alert_value not in ['yes', 'no']:
                await interaction.followup.send("❌ Suspicious Alert must be 'Yes' or 'No' (or leave empty for No)", ephemeral=True)
                return
            sus_alert_boolean = sus_alert_value == "yes"
            row_data = [
                data.get("player_ign", ""),
                data.get("selected_date", ""),
                data.get("selected_rank", ""),
                data.get("selected_status", ""),
                data.get("known_alts", ""),
                data.get("house", ""),
                data.get("discord_id", ""),
                data.get("notes", ""),
                sus_alert_boolean
            ]
            success, message = add_player_to_guild(row_data, interaction.user.name)
            await interaction.followup.send(message, ephemeral=True)
        except Exception as e:
            try:
                await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
            except:
                # If interaction is already responded to, try followup
                try:
                    await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
                except:
                    pass  # If all else fails, just ignore the error

class EditDateSelect(discord.ui.Select):
    def __init__(self):
        options = []
        current_date = datetime.now()
        
        today = current_date.strftime("%m/%d/%Y")
        options.append(discord.SelectOption(label="Today", description=today, value=today))
        
        yesterday = (current_date - timedelta(days=1)).strftime("%m/%d/%Y")
        options.append(discord.SelectOption(label="Yesterday", description=yesterday, value=yesterday))
        
        super().__init__(
            placeholder="Select new join date...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(EditPlayerModalWithDate(self.values[0]))

class EditDatePickerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)  # 60 second timeout
        # Add the date select to this view
        self.add_item(EditDateSelect())

    @discord.ui.button(label="📅 Custom Date", style=discord.ButtonStyle.gray)
    async def custom_date_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CustomEditDateModal())

class EditStatusSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Active, Main", description="Player is active with main account", value="Active, Main"),
            discord.SelectOption(label="Active, Alt", description="Player is active with alternate account", value="Active, Alt"),
            discord.SelectOption(label="Inactive", description="Player is currently inactive", value="Inactive"),
            discord.SelectOption(label="Kicked", description="Player was kicked from the guild", value="Kicked"),
            discord.SelectOption(label="Left", description="Player left the guild", value="Left"),
            discord.SelectOption(label="BANNED", description="Player is banned", value="BANNED")
        ]
        super().__init__(
            placeholder="Select new player status...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Select new join date:",
            view=EditDatePickerView()
        )

class EditPlayerModalWithDate(discord.ui.Modal, title="Edit Player in Masterlist"):
    def __init__(self, selected_date: str):
        super().__init__()
        self.selected_date = selected_date

    player_id = discord.ui.TextInput(
        label="Player ID to Edit",
        placeholder="Enter the player ID to edit",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_data = [self.player_id.value, self.selected_date, "Active, Main"]  # Default status
            success, message = edit_player_in_guild(self.player_id.value, new_data, interaction.user.name)
            await interaction.response.send_message(message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class DateSelect(discord.ui.Select):
    def __init__(self, selected_status: str):
        self.selected_status = selected_status
        # Generate options for recent dates
        options = []
        current_date = datetime.now()
        
        today = current_date.strftime("%m/%d/%Y")
        options.append(discord.SelectOption(label="Today", description=today, value=today))
        
        yesterday = (current_date - timedelta(days=1)).strftime("%m/%d/%Y")
        options.append(discord.SelectOption(label="Yesterday", description=yesterday, value=yesterday))
        
        super().__init__(
            placeholder="Select join date...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_date = self.values[0]
        await interaction.response.edit_message(
            content="Select player rank:",
            view=RankSelectView(self.selected_status, selected_date)
        )

class DatePickerView(discord.ui.View):
    def __init__(self, selected_status: str):
        super().__init__(timeout=60)
        self.selected_status = selected_status
        self.add_item(DateSelect(selected_status))

    @discord.ui.button(label="📅 Custom Date", style=discord.ButtonStyle.gray)
    async def custom_date_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CustomDateModal(self.selected_status))

class RankSelect(discord.ui.Select):
    def __init__(self, selected_status: str, selected_date: str):
        super().__init__(
            placeholder="Select player rank...",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="0 - Endless", value="0 - Endless", emoji="🔴"),
                discord.SelectOption(label="1 - Ultimate Entity", value="1 - Ultimate Entity", emoji="🟠"),
                discord.SelectOption(label="2 - Divine Celestial", value="2 - Divine Celestial", emoji="🟤"),
                discord.SelectOption(label="3 - Omnipotent God", value="3 - Omnipotent God", emoji="🟣"),
                discord.SelectOption(label="4 - Ascending Human", value="4 - Ascending Human", emoji="🟢"),
                discord.SelectOption(label="5 - Lost Soul", value="5 - Lost Soul", emoji="⚫"),
                discord.SelectOption(label="6 - Not in Guild", value="6 - Not in Guild", emoji="⚪"),
            ]
        )
        self.selected_status = selected_status
        self.selected_date = selected_date

    async def callback(self, interaction: discord.Interaction):
        selected_rank = self.values[0]
        await interaction.response.send_modal(AddPlayerModalWithDate(self.selected_date, self.selected_status, selected_rank))

class RankSelectView(discord.ui.View):
    def __init__(self, selected_status: str, selected_date: str):
        super().__init__(timeout=60)
        self.add_item(RankSelect(selected_status, selected_date))

class StatusSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Active, Main", description="Player is active with main account", value="Active, Main"),
            discord.SelectOption(label="Active, Alt", description="Player is active with alternate account", value="Active, Alt"),
            discord.SelectOption(label="Inactive", description="Player is currently inactive", value="Inactive"),
            discord.SelectOption(label="Kicked", description="Player was kicked from the guild", value="Kicked"),
            discord.SelectOption(label="Left", description="Player left the guild", value="Left"),
            discord.SelectOption(label="Banned", description="Player is banned", value="BANNED")
        ]
        super().__init__(
            placeholder="Select player status...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content="Select join date:",
            view=DatePickerView(self.values[0])
        )

class ContinueToStep2View(discord.ui.View):
    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = multi_modal_store.get(interaction.user.id, {})
        await interaction.response.send_modal(
            AddPlayerModalStep2(
                data.get("selected_date", ""),
                data.get("selected_status", ""),
                data.get("selected_rank", ""),
                data.get("player_ign", ""),
                data.get("discord_id", ""),
                data.get("known_alts", ""),
                data.get("house", ""),
                data.get("notes", "")
            )
        )

# For EditPlayerModal
class ContinueToStep2EditView(discord.ui.View):
    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = multi_modal_store.get(interaction.user.id, {})
        await interaction.response.send_modal(
            EditPlayerModalStep2(
                data.get("player_ign", ""),
                data.get("rank", ""),
                data.get("status", ""),
                data.get("discord_id", ""),
                data.get("known_alts", "")
            )
        )

class Watchlist(discord.ui.Modal, title="Add player to Watchlist"):
    def __init__(self, selected_date: str, selected_status: str):
        super().__init__()
        self.selected_date = selected_date
        self.selected_status= selected_status
        # self.selected_reason= selected_reason

    player_ign = discord.ui.TextInput(
        label="IGN (In-Game Name)",
        placeholder="Enter the player's in-game name (e.g., John Doe)",
        required=True,
        max_length=50
    )
    discord_id = discord.ui.TextInput(
        label="Discord ID",
        placeholder="Enter Discord ID (e.g., 551475914809786890)",
        required=False,
        max_length=20
    )
    known_alts = discord.ui.TextInput(
        label="Known Alts",
        placeholder="Enter known alternate accounts (separate with commas)",
        required=False,
        max_length=200
    )
    house = discord.ui.TextInput(
        label="House",
        placeholder="Enter house name",
        required=False,
        max_length=50
    )
    notes = discord.ui.TextInput(
        label="Notes",
        placeholder="Enter any additional notes",
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            multi_modal_store[interaction.user.id] = {
                "player_ign": self.player_ign.value,
                "discord_id": self.discord_id.value or "",
                "known_alts": self.known_alts.value or "",
                "house": self.house.value or "",
                "notes": self.notes.value or "",
                "selected_date": self.selected_date,
                "selected_status": self.selected_status,
            }
            await interaction.response.send_message(
                "Click below to continue..",
                view=WatchlistContinueView(),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class BanStatus(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Select the reason for the ban.",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(label="(ST) Whisper Warning", value="1 - (ST) Whisper Warning", emoji="🟠"),
                discord.SelectOption(label="(ST) Region Warning", value="2 - (ST) Region Warning", emoji="🔴"),
                discord.SelectOption(label="(ST) Banned", value="3 - (ST) Banned", emoji="🟤"),
                discord.SelectOption(label="General Ban", value="General Ban", emoji="🔨"),
                discord.SelectOption(label="Caution", value="Caution", emoji="⚠️"),
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(WatchlistDateSelect(self.values[0]))

        await interaction.response.edit_message(
            content="Select punishment date:",
            view=view
        )

class WatchlistDateSelect(discord.ui.Select):
    def __init__(self, selected_status: str):
        self.selected_status= selected_status
        options = []
        current_date = datetime.now()

        today = current_date.strftime("%m/%d/%Y")
        options.append(discord.SelectOption(label="Today", description=today, value=today))

        yesterday = (current_date - timedelta(days=1)).strftime("%m/%d/%Y")
        options.append(discord.SelectOption(label="Yesterday", description=yesterday, value=yesterday))
        super().__init__(
            placeholder="Select date...",
            min_values=1,
            max_values=1,
            options=options
        )
    async def callback(self, interaction: discord.Interaction):
        selected_date = self.values[0]
        await interaction.response.send_modal(Watchlist(selected_date, self.selected_status))

class WatchlistContinueView(discord.ui.View):
    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = multi_modal_store.get(interaction.user.id, {})
        await interaction.response.send_modal(
            AddWatchlistModalStep2(
                data.get("selected_date", ""),
                data.get("selected_status", ""),
                data.get("selected_rank", ""),
                data.get("player_ign", ""),
                data.get("discord_id", ""),
                data.get("known_alts", ""),
                data.get("house", ""),
                data.get("notes", ""),
                data.get("selected_reason", ""),
            )
        )

class AddWatchlistModalStep2(discord.ui.Modal, title="Add Player to Watchlist - Step 2"):
    def __init__(self, selected_date: str, selected_status: str, selected_rank: str, 
                 player_ign: str, discord_id: str, known_alts: str, house: str, notes: str,
                 screenshot: str):
        super().__init__()
        self.selected_date = selected_date
        self.selected_status = selected_status
        self.selected_rank = selected_rank
        self.player_ign = player_ign
        self.discord_id = discord_id
        self.known_alts = known_alts
        self.house = house
        self.notes = notes
        self.screenshot = screenshot

    guild = discord.ui.TextInput(
        label="Guild",
        placeholder="Enter guild name",
        required=False,
        max_length=50
    )

    #TODO: No clue why, but this is not sending the screenshot link to the sheet
    screenshot = discord.ui.TextInput(
        label="Screenshot URL",
        placeholder="Enter the Discord Message URL(e.g.,https://cdn.discordapp.com/attachments/...)",
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            data = multi_modal_store.pop(interaction.user.id, {})
            row_data = [
                data.get("player_ign", ""),
                data.get("selected_status", ""),
                data.get("guild", ""),
                data.get("selected_date", ""),
                data.get("selected_reason", ""),
                data.get("action_by", ""),
                data.get("notes", ""),
                data.get("screenshot", ""),
                data.get("known_alts", ""),
                data.get("discord_id", ""),
                data.get("house", ""),
            ]
            success, message = add_player_to_banlist(row_data, interaction.user.name)
            await interaction.followup.send(message, ephemeral=True)
        except Exception as e:
            try:
                await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
            except:
                try:
                    await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
                except:
                    pass 

def setup(bot):
    @bot.tree.command(name="create_sheet_menu", description="Create a persistent sheet management menu")
    async def create_sheet_menu(interaction: discord.Interaction):
        embed = discord.Embed(
            title="📊 Sheet Management System",
            description="Click the buttons below to manage players in the Guild Google Sheet",
            color=0x00ff00
        )
        embed.add_field(name="🎯 Masterlist", value="Add, remove, or edit players in the guild list", inline=False)
        embed.add_field(name="🧰 Watchlist", value="Add, remove, or edit players in the watch list", inline=False)
        embed.set_footer(text="All actions are logged automatically on the sheet")

        await interaction.response.send_message("✅ Sheet management menu created!", ephemeral=True)
        await interaction.followup.send(
            embed=embed,
            view=PersistentActionView()
        )

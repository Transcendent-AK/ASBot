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

class AddPlayerModal(discord.ui.Modal, title="Add Player to Masterlist"):
    """
    Modal for adding a player to the Masterlist with all required fields.
    Includes validation for date format and suspicious alert handling.
    """
    player_ign = discord.ui.TextInput(
        label="IGN (In-Game Name)",
        placeholder="Enter the player's in-game name (e.g., John Doe)",
        required=True,
        max_length=50
    )
    join_date = discord.ui.TextInput(
        label="Join Date",
        placeholder="Enter join date (e.g., MM/DD/YYYY)",
        required=True,
        max_length=10
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
    discord_id = discord.ui.TextInput(
        label="Discord ID",
        placeholder="Enter Discord ID (e.g., 551475914809786890)",
        required=False,
        max_length=20
    )
    notes = discord.ui.TextInput(
        label="Notes",
        placeholder="Enter any additional notes",
        required=False,
        max_length=500,
        style=discord.TextStyle.paragraph
    )
    sus_alert = discord.ui.TextInput(
        label="Suspicious Alert (Optional)",
        placeholder="Enter 'Yes' or 'No' for suspicious alert - Leave empty for No",
        required=False,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        """
        Handles form submission for adding a player to the Masterlist.
        Validates date format and suspicious alert, then adds player to sheet.
        
        Args:
            interaction: The Discord interaction object
        """
        try:
            if self.join_date.value.lower() != 'n/a':
                date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
                if not re.match(date_pattern, self.join_date.value):
                    await interaction.response.send_message("❌ Invalid date format. Please use MM/DD/YYYY or 'n/a'", ephemeral=True)
                    return
            
            sus_alert_value = self.sus_alert.value.strip().lower() if self.sus_alert.value else "no"
            if sus_alert_value not in ['yes', 'no']:
                await interaction.response.send_message("❌ Suspicious Alert must be 'Yes' or 'No' (or leave empty for No)", ephemeral=True)
                return
            
            sus_alert_boolean = sus_alert_value == "yes"
            
            row_data = [
                self.player_ign.value,
                self.join_date.value,
                self.rank.value,
                self.status.value,
                self.known_alts.value or "",
                self.house.value or "",
                self.discord_id.value or "",
                self.notes.value or "",
                sus_alert_boolean
            ]
            
            success, message = add_player_to_guild(row_data, interaction.user.name)
            await interaction.response.send_message(message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class RemovePlayerModal(discord.ui.Modal, title="Remove Player from Masterlist"):
    player_id = discord.ui.TextInput(
        label="Player ID to Remove",
        placeholder="Enter the player ID to remove",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            success, message = remove_player_from_guild(self.player_id.value, interaction.user.name)
            await interaction.response.send_message(message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

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
                # Action By is already in the store from the select
            }
            await interaction.response.send_modal(EditPlayerModalStep2())
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class EditPlayerModalStep2(discord.ui.Modal, title="Edit Player in Masterlist - Step 2"):
    sus_alert = discord.ui.TextInput(
        label="Suspicious Alert (Optional)",
        placeholder="Enter 'Yes' or 'No' for suspicious alert - Leave empty for No",
        required=False,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            data = multi_modal_store.pop(interaction.user.id, {})
            action_by_value = data.get('action_by', '')
            sus_alert_value = self.sus_alert.value.strip().lower() if self.sus_alert.value else "no"
            if sus_alert_value not in ['yes', 'no']:
                await interaction.response.send_message("❌ Suspicious Alert must be 'Yes' or 'No' (or leave empty for No)", ephemeral=True)
                return
            sus_alert_boolean = sus_alert_value == "yes"
            # Fetch the current row for the player
            current_row = find_player(data.get("player_ign", ""))
            if not current_row:
                await interaction.response.send_message("❌ Player not found in Masterlist.", ephemeral=True)
                return
            # Merge edited fields into the current row
            # Assuming columns: IGN, Join Date, Rank, Status, Known Alts, House, Discord ID, Notes, Suspicious Alert, Action By
            row_data = [
                data.get("player_ign", current_row[0]),
                current_row[1],  # Join Date (not edited)
                current_row[2],  # Rank (not edited)
                current_row[3],  # Status (not edited)
                data.get("known_alts", current_row[4]),
                data.get("house", current_row[5]),
                data.get("discord_id", current_row[6]),
                data.get("notes", current_row[7]),
                sus_alert_boolean,
                action_by_value
            ]
            success, message = edit_player_in_guild(data.get("player_ign", ""), row_data, action_by_value)
            await interaction.response.send_message(message, ephemeral=True)
            log_update(action_by_value, f"Edited player in Masterlist: {data.get('player_ign', '')}")
        except Exception as e:
            try:
                await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
            except Exception:
                await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

class AddToWatchlistModal(discord.ui.Modal, title="Add Player to Watchlist"):
    player_ign = discord.ui.TextInput(
        label="IGN (In-Game Name)",
        placeholder="Enter the player's in-game name (e.g., John Doe)",
        required=True,
        max_length=50
    )
    status = discord.ui.TextInput(
        label="Status",
        placeholder="Enter status (e.g., General Ban, Warning, Active)",
        required=True,
        max_length=50
    )
    guild = discord.ui.TextInput(
        label="Guild",
        placeholder="Enter guild name (e.g., Puffles)",
        required=True,
        max_length=50
    )
    status_date = discord.ui.TextInput(
        label="Status Date",
        placeholder="Enter status date (e.g., MM/DD/YYYY)",
        required=True,
        max_length=10
    )
    reason = discord.ui.TextInput(
        label="Reason for Status",
        placeholder="Enter reason (e.g., ST - Leeching, Harassment)",
        required=True,
        max_length=100
    )
    action_by = discord.ui.TextInput(
        label="Action By",
        placeholder="Enter who took the action (e.g., Admin, Moderator)",
        required=True,
        max_length=50
    )
    other_notes = discord.ui.TextInput(
        label="Other Notes",
        placeholder="Enter additional notes",
        required=False,
        max_length=500,
        style=discord.TextStyle.paragraph
    )
    screenshots = discord.ui.TextInput(
        label="Screenshots",
        placeholder="Enter screenshot URL (e.g., https://discord.com/channels/...)",
        required=False,
        max_length=200
    )
    known_alts = discord.ui.TextInput(
        label="Known Alts",
        placeholder="Enter known alternate accounts (separate with commas)",
        required=False,
        max_length=200
    )
    discord_id = discord.ui.TextInput(
        label="Discord ID",
        placeholder="Enter Discord ID (e.g., 551475914809786890)",
        required=False,
        max_length=20
    )
    house_name = discord.ui.TextInput(
        label="House Name",
        placeholder="Enter house name",
        required=False,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validate date format
            date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
            if not re.match(date_pattern, self.status_date.value):
                await interaction.response.send_message("❌ Invalid date format. Please use MM/DD/YYYY", ephemeral=True)
                return
            
            row_data = [
                self.player_ign.value,
                self.status.value,
                self.guild.value,
                self.status_date.value,
                self.reason.value,
                self.action_by.value,
                self.other_notes.value or "",
                self.screenshots.value or "",
                self.known_alts.value or "",
                self.discord_id.value or "",
                self.house_name.value or ""
            ]
            
            success, message = add_player_to_banlist(row_data, interaction.user.name)
            await interaction.response.send_message(message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

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
            # Validate date format
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
                "Click below to continue.",
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
        try:
            data = multi_modal_store.pop(interaction.user.id, {})
            sus_alert_value = self.sus_alert.value.strip().lower() if self.sus_alert.value else "no"
            if sus_alert_value not in ['yes', 'no']:
                await interaction.response.send_message("❌ Suspicious Alert must be 'Yes' or 'No' (or leave empty for No)", ephemeral=True)
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
            await interaction.response.send_message(message, ephemeral=True)
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

class WatchlistStatusSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1- (ST) Whisper Warning", description="First strike - whisper warning", value="1- (ST) Whisper Warning"),
            discord.SelectOption(label="2- (ST) Region Warning", description="Second strike - region warning", value="2- (ST) Region Warning"),
            discord.SelectOption(label="3- (ST) Banned", description="Third strike - banned", value="3- (ST) Banned"),
            discord.SelectOption(label="General Ban", description="General ban status", value="General Ban"),
            discord.SelectOption(label="Caution", description="Caution status", value="Caution")
        ]
        super().__init__(
            placeholder="Select player status...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(WatchlistReasonSelect(self.values[0]))
        await interaction.response.edit_message(
            content="Select reason for status:",
            view=view
        )

class WatchlistReasonSelect(discord.ui.Select):
    def __init__(self, selected_status: str):
        self.selected_status = selected_status
        options = [
            discord.SelectOption(label="ST - Leeching", description="Suspicious trading - leeching", value="ST - Leeching"),
            discord.SelectOption(label="ST - Not Following Instructions", description="Not following suspicious trading instructions", value="ST - Not Following Instructions"),
            discord.SelectOption(label="Making Trouble", description="General trouble making behavior", value="Making Trouble"),
            discord.SelectOption(label="ST - Not Responding to Warnings", description="Not responding to suspicious trading warnings", value="ST - Not Responding to Warnings"),
            discord.SelectOption(label="ST - Banned in Other Raids", description="Banned in other raids for suspicious trading", value="ST - Banned in Other Raids"),
            discord.SelectOption(label="Suspicious Person", description="Generally suspicious behavior", value="Suspicious Person"),
            discord.SelectOption(label="Scammer", description="Scamming behavior", value="Scammer"),
            discord.SelectOption(label="Big Drama Llama", description="Drama causing behavior", value="Big Drama Llama"),
            discord.SelectOption(label="Griefing", description="Griefing behavior", value="Griefing"),
            discord.SelectOption(label="VOE Issue", description="Voice of Experience issue", value="VOE Issue"),
            discord.SelectOption(label="Kyzey's Shit List", description="On Kyzey's list", value="Kyzey's Shit List")
        ]
        super().__init__(
            placeholder="Select reason for status...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(ActionBySelect(self.selected_status, self.values[0]))
        await interaction.response.edit_message(
            content="Select who took the action:",
            view=view
        )

class ActionBySelect(discord.ui.Select):
    def __init__(self, selected_status: str, selected_reason: str):
        self.selected_status = selected_status
        self.selected_reason = selected_reason
        
        # Get dynamic action by list from the sheet
        from utils.watchlist_ops import get_action_by_list
        action_by_list = get_action_by_list()
        
        options = []
        for action_by in action_by_list:
            options.append(discord.SelectOption(
                label=action_by, 
                description=f"Action taken by {action_by}", 
                value=action_by
            ))
        
        super().__init__(
            placeholder="Select who took the action...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AddToWatchlistModalWithActionBy(
            self.selected_status, 
            self.selected_reason, 
            self.values[0]
        ))

class AddToWatchlistModalWithActionBy(discord.ui.Modal, title="Add Player to Watchlist - Step 1"):
    def __init__(self, selected_status: str, selected_reason: str, selected_action_by: str):
        super().__init__()
        self.selected_status = selected_status
        self.selected_reason = selected_reason
        self.selected_action_by = selected_action_by

    player_ign = discord.ui.TextInput(
        label="IGN (In-Game Name)",
        placeholder="Enter the player's in-game name (e.g., John Doe)",
        required=True,
        max_length=50
    )
    guild = discord.ui.TextInput(
        label="Guild",
        placeholder="Enter guild name (e.g., Transcendent)",
        required=False,
        max_length=50
    )
    status_date = discord.ui.TextInput(
        label="Status Date",
        placeholder="Enter status date (e.g., MM/DD/YYYY)",
        required=True,
        max_length=10
    )
    other_notes = discord.ui.TextInput(
        label="Other Notes",
        placeholder="Enter additional notes",
        required=False,
        max_length=500
    )
    screenshots = discord.ui.TextInput(
        label="Screenshots",
        placeholder="Enter screenshot URL (e.g., https://discord.com/channels/...)",
        required=False,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validate date format
            date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
            if not re.match(date_pattern, self.status_date.value):
                await interaction.response.send_message("❌ Invalid date format. Please use MM/DD/YYYY", ephemeral=True)
                return
            
            # Store the data and show the second modal
            await interaction.response.send_modal(AddToWatchlistModalStep2(
                self.selected_status,
                self.selected_reason,
                self.selected_action_by,
                self.player_ign.value,
                self.guild.value or "",
                self.status_date.value,
                self.other_notes.value or "",
                self.screenshots.value or ""
            ))
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class AddToWatchlistModalStep2(discord.ui.Modal, title="Add Player to Watchlist - Step 2"):
    def __init__(self, selected_status: str, selected_reason: str, selected_action_by: str,
                 player_ign: str, guild: str, status_date: str, other_notes: str, screenshots: str):
        super().__init__()
        self.selected_status = selected_status
        self.selected_reason = selected_reason
        self.selected_action_by = selected_action_by
        self.player_ign = player_ign
        self.guild = guild
        self.status_date = status_date
        self.other_notes = other_notes
        self.screenshots = screenshots

    known_alts = discord.ui.TextInput(
        label="Known Alts",
        placeholder="Enter known alternate accounts (separate with commas)",
        required=False,
        max_length=200
    )
    discord_id = discord.ui.TextInput(
        label="Discord ID",
        placeholder="Enter Discord ID (e.g., 551475914809786890)",
        required=False,
        max_length=20
    )
    house_name = discord.ui.TextInput(
        label="House Name",
        placeholder="Enter house name",
        required=False,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            row_data = [
                self.player_ign,
                self.selected_status,
                self.guild,
                self.status_date,
                self.selected_reason,
                self.selected_action_by,
                self.other_notes,
                self.screenshots,
                self.known_alts.value or "",
                self.discord_id.value or "",
                self.house_name.value or ""
            ]
            
            success, message = add_player_to_banlist(row_data, interaction.user.name)
            await interaction.response.send_message(message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

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

    @discord.ui.button(label="Add to Watchlist", style=discord.ButtonStyle.red, custom_id="persistent_watchlist_add")
    async def watchlist_add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Create a view with the select menu
            view = discord.ui.View()
            view.add_item(WatchlistStatusSelect())
            await interaction.response.send_message(
                "Select player status:",
                view=view,
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error opening select menu: {str(e)}", ephemeral=True)

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

# For AddToWatchlistModalWithActionBy
class ContinueToStep2WatchlistView(discord.ui.View):
    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = multi_modal_store.get(interaction.user.id, {})
        await interaction.response.send_modal(
            AddToWatchlistModalStep2(
                data.get("selected_status", ""),
                data.get("selected_reason", ""),
                data.get("selected_action_by", ""),
                data.get("player_ign", ""),
                data.get("guild", ""),
                data.get("status_date", ""),
                data.get("other_notes", ""),
                data.get("screenshots", "")
            )
        )

def setup(bot):
    @bot.tree.command(name="create_sheet_menu", description="Create a persistent sheet management menu")
    async def create_sheet_menu(interaction: discord.Interaction):
        embed = discord.Embed(
            title="📊 Sheet Management System",
            description="Click the buttons below to manage players in the Google Sheet",
            color=0x00ff00
        )
        embed.add_field(name="🎯 Masterlist", value="Add, remove, or edit players in the guild list", inline=False)
        embed.add_field(name="⚠️ Watchlist", value="Manage banned or watched players", inline=False)
        embed.set_footer(text="All actions are logged automatically")

        await interaction.response.send_message("✅ Sheet management menu created!", ephemeral=True)
        await interaction.followup.send(
            embed=embed,
            view=PersistentActionView()
        )
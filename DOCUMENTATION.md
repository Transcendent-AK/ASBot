# ASBot Documentation

## Overview
ASBot is a Discord bot designed to manage player data in Google Sheets. It provides an interactive interface for adding, editing, and removing players from both Masterlist and Watchlist sheets.

## File Structure

### Core Files
- `bot_controller.py` - Main bot entry point and event handlers
- `commands/sheet.py` - Sheet management commands and UI components
- `commands/ping.py` - Simple ping command for testing

### Utility Files
- `utils/google_sheet.py` - Google Sheets API integration
- `utils/masterlist_ops.py` - Masterlist sheet operations
- `utils/watchlist_ops.py` - Watchlist sheet operations
- `utils/update_log_ops.py` - Update logging functionality

## Core Functions

### Bot Controller (`bot_controller.py`)

#### `on_ready()`
Event handler for when the bot is ready and connected to Discord.
- Displays bot information and guild details
- Shows permission status for each guild
- Logs connection status

#### `on_command_error(ctx, error)`
Event handler for command errors.
- Logs command errors to console

#### `on_app_command_error(interaction, error)`
Event handler for slash command errors.
- Logs errors and sends error message to user

### Google Sheets Integration (`utils/google_sheet.py`)

#### `get_client()`
Creates and returns an authenticated Google Sheets client.
- Attempts to load credentials from file path or JSON content
- Returns: `gspread.Client` - Authenticated Google Sheets client
- Raises: `ValueError` if credentials cannot be loaded

#### `get_sheet(sheet_name)`
Gets a specific worksheet from the Google Spreadsheet.
- Args: `sheet_name (str)` - Name of the worksheet to retrieve
- Returns: `gspread.Worksheet` - The requested worksheet object

### Update Logging (`utils/update_log_ops.py`)

#### `log_update(user_name, change_description)`
Logs an update to the Update Sheet with timestamp and user information.
- Args: 
  - `user_name (str)` - Name of the user who made the change
  - `change_description (str)` - Description of the change made

#### `get_recent_updates(limit=10)`
Retrieves recent updates from the Update Sheet.
- Args: `limit (int)` - Number of recent updates to retrieve (default: 10)
- Returns: `list` - List of recent update rows from the sheet

### Masterlist Operations (`utils/masterlist_ops.py`)

#### `add_player_to_guild(row_data, user_name)`
Adds a player to the Masterlist sheet.
- Args:
  - `row_data (list)` - Player data to add to the sheet
  - `user_name (str)` - Name of the user making the change
- Returns: `tuple` - (success (bool), message (str))

#### `remove_player_from_guild(player_id, user_name)`
Removes a player from the Masterlist sheet by ID.
- Args:
  - `player_id (str)` - ID of the player to remove
  - `user_name (str)` - Name of the user making the change
- Returns: `tuple` - (success (bool), message (str))

#### `edit_player_in_guild(player_id, new_data, user_name)`
Edits a player's data in the Masterlist sheet.
- Args:
  - `player_id (str)` - ID of the player to edit
  - `new_data (list)` - New player data
  - `user_name (str)` - Name of the user making the change
- Returns: `tuple` - (success (bool), message (str))

#### `get_all_players()`
Retrieves all players from the Masterlist sheet.
- Returns: `list` - All player data from the Masterlist sheet

#### `find_player(player_id)`
Finds a specific player in the Masterlist sheet.
- Args: `player_id (str)` - ID of the player to find
- Returns: `list or None` - Player data if found, None if not found

### Watchlist Operations (`utils/watchlist_ops.py`)

#### `get_action_by_list()`
Gets the list of Action By users from the sheet dropdown options.
- Returns: `list` - Predefined Action By options from the Google Sheet dropdown

#### `add_player_to_banlist(row_data, user_name)`
Adds a player to the Watchlist sheet.
- Args:
  - `row_data (list)` - Player data to add to the watchlist
  - `user_name (str)` - Name of the user making the change
- Returns: `tuple` - (success (bool), message (str))

#### `remove_player_from_banlist(player_id, user_name)`
Removes a player from the Watchlist sheet by ID.
- Args:
  - `player_id (str)` - ID of the player to remove
  - `user_name (str)` - Name of the user making the change
- Returns: `tuple` - (success (bool), message (str))

#### `edit_player_in_banlist(player_id, new_data, user_name)`
Edits a player's data in the Watchlist sheet.
- Args:
  - `player_id (str)` - ID of the player to edit
  - `new_data (list)` - New player data
  - `user_name (str)` - Name of the user making the change
- Returns: `tuple` - (success (bool), message (str))

#### `get_all_banned_players()`
Retrieves all players from the Watchlist sheet.
- Returns: `list` - All player data from the Watchlist sheet

#### `find_banned_player(player_id)`
Finds a specific player in the Watchlist sheet.
- Args: `player_id (str)` - ID of the player to find
- Returns: `list or None` - Player data if found, None if not found

#### `is_player_banned(player_id)`
Checks if a player is in the Watchlist.
- Args: `player_id (str)` - ID of the player to check
- Returns: `bool` - True if player is banned, False otherwise

## UI Components (`commands/sheet.py`)

### Modal Classes

#### `AddPlayerModal`
Modal for adding a player to the Masterlist with all required fields.
- Includes validation for date format and suspicious alert handling
- Fields: IGN, Join Date, Rank, Status, Known Alts, House, Discord ID, Notes, Suspicious Alert

#### `RemovePlayerModal`
Modal for removing a player from the Masterlist.
- Fields: Player ID to Remove

#### `EditPlayerModal`
Modal for editing a player in the Masterlist.
- Fields: Player IGN, New Rank, New Status, Discord ID, Suspicious Alert

#### `AddToWatchlistModal`
Modal for adding a player to the Watchlist.
- Fields: IGN, Status, Guild, Status Date, Reason, Action By, Other Notes, Screenshots, Known Alts, Discord ID, House Name

#### `AddPlayerModalWithDate`
Modal for adding a player with pre-selected date, status, and rank.
- Used in the multi-step add player flow
- Fields: IGN, Discord ID, Suspicious Alert

### Select Components

#### `StatusSelect`
Dropdown for selecting player status.
- Options: Active Main, Active Alt, Inactive, Kicked, Left, Banned

#### `RankSelect`
Dropdown for selecting player rank with emojis.
- Options: 0-6 with corresponding emojis and descriptions

#### `DateSelect`
Dropdown for selecting join date.
- Options: Today, Yesterday

#### `WatchlistStatusSelect`
Dropdown for selecting watchlist status.
- Options: Various warning and ban statuses

#### `WatchlistReasonSelect`
Dropdown for selecting watchlist reason.
- Options: Various reasons for watchlist entries

#### `ActionBySelect`
Dropdown for selecting who took the action.
- Options: Dynamic list from sheet or predefined list

### View Components

#### `PersistentActionView`
Persistent view with buttons for all sheet operations.
- Buttons: Add Player, Remove Player, Edit Player, Add to Watchlist

#### `DatePickerView`
View for date selection with custom date option.
- Components: DateSelect dropdown, Custom Date button

#### `RankSelectView`
View for rank selection.
- Components: RankSelect dropdown

## Commands

### `/ping`
Simple command to check bot latency.
- Returns: Bot latency in milliseconds

### `/create_sheet_menu`
Creates a persistent sheet management menu.
- Creates an embed with description and buttons
- Sets up PersistentActionView for ongoing interactions

## Data Flow

### Add Player Flow
1. User clicks "Add Player to Masterlist"
2. StatusSelect shows status options
3. DatePickerView shows date options
4. RankSelect shows rank options
5. AddPlayerModalWithDate collects remaining data
6. Player is added to Masterlist sheet
7. Update is logged to Update Sheet

### Add to Watchlist Flow
1. User clicks "Add to Watchlist"
2. WatchlistStatusSelect shows status options
3. WatchlistReasonSelect shows reason options
4. ActionBySelect shows action by options
5. AddToWatchlistModalWithActionBy collects remaining data
6. Player is added to Watchlist sheet
7. Update is logged to Update Sheet

## Error Handling

- All operations include try-catch blocks
- User-friendly error messages are displayed
- Errors are logged to console
- Failed operations return appropriate error messages

## Security Features

- All interactions are ephemeral (private to user)
- Input validation for dates and suspicious alert
- Boolean conversion for checkbox fields
- Proper error handling prevents crashes

## Environment Variables

- `BOT_TOKEN` - Discord bot token
- `SPREADSHEET_ID` - Google Sheets spreadsheet ID
- `GOOGLE_SERVICE_ACCOUNT_JSON` - Google service account credentials

## Dependencies

- `discord.py` - Discord bot framework
- `gspread` - Google Sheets API
- `python-dotenv` - Environment variable management
- `google-auth` - Google authentication 
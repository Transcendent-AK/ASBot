from .google_sheet import get_sheet
from .update_log_ops import log_update

def get_action_by_list():
    """Get the list of Action By users from the sheet"""
    try:
        # Assuming you have a sheet or range with the Action By list
        # You'll need to specify the correct sheet name and range
        sheet = get_sheet('Action By List')  # or whatever sheet contains this list
        values = sheet.get_all_values()
        # Flatten the list and remove empty values
        action_by_list = [row[0] for row in values if row[0].strip()]
        return action_by_list
    except Exception as e:
        # Fallback to default list if sheet doesn't exist
        print(f"Warning: Could not load Action By list from sheet: {e}")
        return ["Gds", "Beaako", "Skar", "Kyzey", "Nyx", "Kitsu", "Exchibi", "Luna", "Lof", "Kahz", "Bogi"]

def add_player_to_banlist(row_data, user_name):
    """Add a player to the Watchlist"""
    try:
        sheet = get_sheet('Watchlist')
        sheet.append_row(row_data)
        log_update(user_name, f"Added player to Watchlist: {row_data}")
        return True, f"✅ Successfully added player to Watchlist!"
    except Exception as e:
        return False, f"❌ Failed to add player to Watchlist: {str(e)}"

def remove_player_from_banlist(player_id, user_name):
    """Remove a player from the Watchlist by ID"""
    sheet = get_sheet('Watchlist')
    try:
        cell = sheet.find(player_id)
        sheet.delete_rows(cell.row)
        log_update(user_name, f"Removed player from Watchlist: {player_id}")
        return True
    except:
        return False

def edit_player_in_banlist(player_id, new_data, user_name):
    """Edit a player's data in the Watchlist"""
    sheet = get_sheet('Watchlist')
    try:
        cell = sheet.find(player_id)
        # Update the row with new data
        sheet.update(f'A{cell.row}:Z{cell.row}', [new_data])
        log_update(user_name, f"Edited player in Watchlist: {player_id}")
        return True
    except:
        return False

def get_all_banned_players():
    """Get all players from the Watchlist"""
    sheet = get_sheet('Watchlist')
    return sheet.get_all_values()

def find_banned_player(player_id):
    """Find a specific player in the Watchlist"""
    sheet = get_sheet('Watchlist')
    try:
        cell = sheet.find(player_id)
        row = sheet.row_values(cell.row)
        return row
    except:
        return None

def is_player_banned(player_id):
    """Check if a player is in the Watchlist"""
    return find_banned_player(player_id) is not None 
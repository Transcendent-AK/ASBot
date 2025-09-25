from .google_sheet import get_sheet
from .update_log_ops import log_update

def add_player_to_banlist(player_id, user_name):
    """
    Adds a player to the Watchlist sheet.
    
    Args:
        row_data (list): Player data to add to the watchlist
        user_name (str): Name of the user making the change
        
    Returns:
        tuple: (success (bool), message (str))
    """
    try:
        sheet = get_sheet('Watchlist')
        cell = sheet.find(player_id)
        sheet.append_row(cell.row) #TODO: add the name of the admin that added the player on the action by
        log_update(user_name, f"Added player to Watchlist: {player_id}")
        return True, f"✅ Successfully added player {player_id} to Watchlist!"
    except Exception as e:
        return False, f"❌ Failed to add player to Watchlist: {str(e)}"

def remove_player_from_banlist(player_id, user_name):
    """
    Removes a player from the Watchlist sheet by ID.
    
    Args:
        player_id (str): ID of the player to remove
        user_name (str): Name of the user making the change
        
    Returns:
        tuple: (success (bool), message (str))
    """
    sheet = get_sheet('Watchlist')
    try:
        cell = sheet.find(player_id)
        sheet.delete_rows(cell.row)
        log_update(user_name, f"Removed player from Watchlist: {player_id}")
        return True, f"✅ Successfully removed {player_id} from Watchlist!"
    except Exception as e:
        return False, f"❌ Error removing player from Watchlist: {str(e)}"

def edit_player_in_banlist(player_id, new_data, user_name):
    """
    Edits a player's data in the Watchlist sheet.
    
    Args:
        player_id (str): ID of the player to edit
        new_data (list): New player data
        user_name (str): Name of the user making the change
        
    Returns:
        tuple: (success (bool), message (str))
    """
    sheet = get_sheet('Watchlist')
    try:
        cell = sheet.find(player_id)
        sheet.update(f'A{cell.row}:Z{cell.row}', [new_data])
        log_update(user_name, f"Edited player in Watchlist: {player_id}")
        return True, f"✅ Successfully edited {player_id} in Watchlist!"
    except Exception as e:
        return False, f"❌ Error editing player in Watchlist: {str(e)}"

def get_all_banned_players():
    """
    Retrieves all players from the Watchlist sheet.
    
    Returns:
        list: All player data from the Watchlist sheet
    """
    sheet = get_sheet('Watchlist')
    return sheet.get_all_values()

def find_banned_player(player_id):
    """
    Finds a specific player in the Watchlist sheet.
    
    Args:
        player_id (str): ID of the player to find
        
    Returns:
        list or None: Player data if found, None if not found
    """
    sheet = get_sheet('Watchlist')
    try:
        cell = sheet.find(player_id)
        row = sheet.row_values(cell.row)
        return row
    except:
        return None

def is_player_banned(player_id):
    """
    Checks if a player is in the Watchlist.
    
    Args:
        player_id (str): ID of the player to check
        
    Returns:
        bool: True if player is banned, False otherwise
    """
    return find_banned_player(player_id) is not None 

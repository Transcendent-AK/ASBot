from .google_sheet import get_sheet
from .update_log_ops import log_update

def add_player_to_guild(row_data, user_name):
    """
    Adds a player to the Masterlist sheet.
    
    Args:
        row_data (list): Player data to add to the sheet
        user_name (str): Name of the user making the change
        
    Returns:
        tuple: (success (bool), message (str))
    """
    try:
        sheet = get_sheet('Masterlist')
        sheet.append_row(row_data)
        log_update(user_name, f"Added player to Masterlist: {row_data[0]}")
        return True, f"✅ Successfully added {row_data[0]} to Masterlist!"
    except Exception as e:
        return False, f"❌ Error adding player to Masterlist: {str(e)}"

def remove_player_from_guild(player_id, user_name):
    """
    Removes a player from the Masterlist sheet by ID.
    
    Args:
        player_id (str): ID of the player to remove
        user_name (str): Name of the user making the change
        
    Returns:
        tuple: (success (bool), message (str))
    """
    sheet = get_sheet('Masterlist')
    try:
        cell = sheet.find(player_id)
        sheet.delete_rows(cell.row)
        log_update(user_name, f"Removed player from Masterlist: {player_id}")
        return True, f"✅ Successfully removed {player_id} from Masterlist!"
    except Exception as e:
        return False, f"❌ Error removing player from Masterlist: {str(e)}"

def edit_player_in_guild(player_id, new_data, user_name):
    """
    Edits a player's data in the Masterlist sheet.
    
    Args:
        player_id (str): ID of the player to edit
        new_data (list): New player data
        user_name (str): Name of the user making the change
        
    Returns:
        tuple: (success (bool), message (str))
    """
    sheet = get_sheet('Masterlist')
    try:
        cell = sheet.find(player_id)
        sheet.update(f'A{cell.row}:Z{cell.row}', [new_data])
        log_update(user_name, f"Edited player in Masterlist: {player_id}")
        return True, f"✅ Successfully edited {player_id} in Masterlist!"
    except Exception as e:
        return False, f"❌ Error editing player in Masterlist: {str(e)}"

def get_all_players():
    """
    Retrieves all players from the Masterlist sheet.
    
    Returns:
        list: All player data from the Masterlist sheet
    """
    sheet = get_sheet('Masterlist')
    return sheet.get_all_values()

def find_player(player_id):
    """
    Finds a specific player in the Masterlist sheet.
    
    Args:
        player_id (str): ID of the player to find
        
    Returns:
        list or None: Player data if found, None if not found
    """
    sheet = get_sheet('Masterlist')
    try:
        cell = sheet.find(player_id)
        row = sheet.row_values(cell.row)
        return row
    except:
        return None 

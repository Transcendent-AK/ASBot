from .google_sheet import get_sheet
from .update_log_ops import log_update

def add_player_to_guild(row_data, user_name):
    """Add a player to the Masterlist"""
    sheet = get_sheet('Masterlist')
    sheet.append_row(row_data)
    log_update(user_name, f"Added player to Masterlist: {row_data}")

def remove_player_from_guild(player_id, user_name):
    """Remove a player from the Masterlist by ID"""
    sheet = get_sheet('Masterlist')
    # Find the row with the player_id and delete it
    try:
        cell = sheet.find(player_id)
        sheet.delete_rows(cell.row)
        log_update(user_name, f"Removed player from Masterlist: {player_id}")
        return True
    except:
        return False

def edit_player_in_guild(player_id, new_data, user_name):
    """Edit a player's data in the Masterlist"""
    sheet = get_sheet('Masterlist')
    try:
        cell = sheet.find(player_id)
        # Update the row with new data
        sheet.update(f'A{cell.row}:Z{cell.row}', [new_data])
        log_update(user_name, f"Edited player in Masterlist: {player_id}")
        return True
    except:
        return False

def get_all_players():
    """Get all players from the Masterlist"""
    sheet = get_sheet('Masterlist')
    return sheet.get_all_values()

def find_player(player_id):
    """Find a specific player in the Masterlist"""
    sheet = get_sheet('Masterlist')
    try:
        cell = sheet.find(player_id)
        row = sheet.row_values(cell.row)
        return row
    except:
        return None 
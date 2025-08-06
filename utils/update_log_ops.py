from datetime import datetime

from .google_sheet import get_sheet

def log_update(user_name, change_description):
    """
    Logs an update to the Update Sheet with timestamp and user information.
    
    Args:
        user_name (str): Name of the user who made the change
        change_description (str): Description of the change made
    """
    sheet = get_sheet('Update Sheet')
    date_str = datetime.now().strftime('%Y/%m/%d')
    sheet.append_row([date_str, user_name, change_description])

def get_recent_updates(limit=10):
    """
    Retrieves recent updates from the Update Sheet.
    
    Args:
        limit (int): Number of recent updates to retrieve (default: 10)
        
    Returns:
        list: List of recent update rows from the sheet
    """
    sheet = get_sheet('Update Sheet')
    all_values = sheet.get_all_values()
    return all_values[-limit:] if len(all_values) > limit else all_values 

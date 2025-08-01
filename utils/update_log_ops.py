from datetime import datetime
from .google_sheet import get_sheet

def log_update(user_name, change_description):
    """Log an update to the Update Sheet"""
    sheet = get_sheet('Update Sheet')
    date_str = datetime.now().strftime('%Y/%m/%d')
    sheet.append_row([date_str, user_name, change_description])

def get_recent_updates(limit=10):
    """Get recent updates from the Update Sheet"""
    sheet = get_sheet('Update Sheet')
    # Get the last 'limit' rows
    all_values = sheet.get_all_values()
    return all_values[-limit:] if len(all_values) > limit else all_values 
from datetime import datetime

from .google_sheet import get_sheet

def log_update(user_name, change_description):
    """
    Logs an update to the Update Sheet with timestamp and user information.
    
    Args:
        user_name (str): Name of the user who made the change
        change_description (str): Description of the change made
    """

    #HardCoded admin names
    if user_name == 'kahzukie':
        user_name = 'Kahz'

    if user_name == '.onlyman':
        user_name = 'Beaako'

    if user_name == 'gds_':
        user_name = 'Gds'

    if user_name == 'wpmz':
        user_name = 'Exdel'

    if user_name == 'skar_8685':
        user_name = 'Skar'

    if user_name == 'reginaphalange9799':
        user_name = 'Luna'

    if user_name == 'kitsuneblaze0592':
        user_name = 'Kitsu'

    if user_name == 'night.flower':
        user_name = 'Nyx'

    if user_name == 'kyzeyy':
        user_name = 'Kyzey'

    if user_name == 'voyagerloaf':
        user_name = 'Lof'

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

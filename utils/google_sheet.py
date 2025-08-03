import os
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

def get_client():
    """
    Creates and returns an authenticated Google Sheets client.
    
    Attempts to load credentials from either a file path or JSON content.
    
    Returns:
        gspread.Client: Authenticated Google Sheets client
        
    Raises:
        ValueError: If credentials cannot be loaded
    """
    try:
        if os.path.exists(SERVICE_ACCOUNT_JSON):
            credentials = Credentials.from_service_account_file(
                SERVICE_ACCOUNT_JSON,
                scopes=SCOPES
            )
        else:
            try:
                service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
                credentials = Credentials.from_service_account_info(
                    service_account_info,
                    scopes=SCOPES
                )
            except (json.JSONDecodeError, TypeError):
                raise ValueError(f"GOOGLE_SERVICE_ACCOUNT_JSON must be either a valid file path or JSON content. Current value: {SERVICE_ACCOUNT_JSON}")
        
        return gspread.authorize(credentials)
    except Exception as e:
        print(f"Error setting up Google credentials: {e}")
        print(f"SERVICE_ACCOUNT_JSON value: {SERVICE_ACCOUNT_JSON}")
        print(f"SPREADSHEET_ID value: {SPREADSHEET_ID}")
        raise

def get_sheet(sheet_name):
    """
    Gets a specific worksheet from the Google Spreadsheet.
    
    Args:
        sheet_name (str): Name of the worksheet to retrieve
        
    Returns:
        gspread.Worksheet: The requested worksheet object
    """
    client = get_client()
    return client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
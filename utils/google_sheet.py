import os
import gspread
from google.oauth2.service_account import Credentials

# Set up the credentials and client
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") 

def get_client():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return gspread.authorize(credentials)

def get_sheet(sheet_name):
    """Get a specific worksheet from the Admin Sheet"""
    client = get_client()
    return client.open('#Admin Sheet').worksheet(sheet_name)
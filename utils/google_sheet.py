import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Set up the credentials and client
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") 

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)
client = gspread.authorize(credentials)

def log_update(user_name, change_description):
    sheet = client.open('#Admin Sheet').worksheet('Update Sheet')
    date_str = datetime.now().strftime('%Y/%m/%d')
    sheet.append_row([date_str, user_name, change_description])

def add_player_to_guild(sheet_name, row_data, user_name):
    sheet = client.open('#Admin Sheet').worksheet('Masterlist')
    sheet.append_row(row_data)
    log_update(user_name, f"Added player: {row_data}")
    
def add_player_to_banlist(sheet_name, row_data, user_name):
    sheet = client.open('#Admin Sheet').worksheet('Watchlist')
    sheet.append_row(row_data)
    log_update(user_name, f"Added to banlist: {row_data}")
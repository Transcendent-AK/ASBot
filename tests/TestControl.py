import os
import json
import unittest
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
import discord
import asyncio

# Load environment variables
load_dotenv()

class TestEnvVariables(unittest.TestCase):

    def test_bot_token_present(self):
        """Check if BOT_TOKEN is set and not empty"""
        bot_token = os.getenv("BOT_TOKEN")
        self.assertIsNotNone(bot_token, "BOT_TOKEN is not set")
        self.assertNotEqual(bot_token.strip(), "", "BOT_TOKEN is empty")

    def test_google_service_account_json_present(self):
        """Check if GOOGLE_SERVICE_ACCOUNT_JSON is set and valid JSON"""
        json_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        self.assertIsNotNone(json_str, "GOOGLE_SERVICE_ACCOUNT_JSON is not set")
        self.assertNotEqual(json_str.strip(), "", "GOOGLE_SERVICE_ACCOUNT_JSON is empty")

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            self.fail(f"GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON: {e}")

        required_keys = [
            "type", "project_id", "private_key_id",
            "private_key", "client_email", "client_id"
        ]
        for key in required_keys:
            self.assertIn(key, data, f"Missing key in GOOGLE_SERVICE_ACCOUNT_JSON: {key}")

    def test_spreadsheet_id_present(self):
        """Check if SPREADSHEET_ID is set and not empty"""
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        self.assertIsNotNone(spreadsheet_id, "SPREADSHEET_ID is not set")
        self.assertNotEqual(spreadsheet_id.strip(), "", "SPREADSHEET_ID is empty")

    def test_can_access_spreadsheet(self):
        """Check if the service account can access the spreadsheet"""
        json_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        spreadsheet_id = os.getenv("SPREADSHEET_ID")

        self.assertIsNotNone(json_str, "GOOGLE_SERVICE_ACCOUNT_JSON is not set")
        self.assertIsNotNone(spreadsheet_id, "SPREADSHEET_ID is not set")

        try:
            credentials_dict = json.loads(json_str)
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON: {e}")

        try:
            creds = Credentials.from_service_account_info(
                credentials_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
            )
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(spreadsheet_id)

            # Just checking if we can read the title of the spreadsheet
            title = spreadsheet.title
            self.assertIsInstance(title, str)
            print(f"✅ Accessed spreadsheet: {title}")

        except Exception as e:
            self.fail(f"Failed to access spreadsheet: {e}")


    def test_discord_bot_token_works(self):
        """Test if the Discord BOT_TOKEN is valid by logging in and fetching bot user info"""

        token = os.getenv("BOT_TOKEN")
        self.assertIsNotNone(token, "BOT_TOKEN is not set")
        self.assertNotEqual(token.strip(), "", "BOT_TOKEN is empty")

        # Inner coroutine to run the Discord client logic
        async def run_bot_test():
            intents = discord.Intents.none()
            client = discord.Client(intents=intents)

            # Define a future to capture bot user info
            bot_info_future = asyncio.Future()

            @client.event
            async def on_ready():
                # Set the result to bot user once connected
                bot_info_future.set_result(client.user)
                await client.close()  # Disconnect after retrieving user info

            try:
                await client.start(token)
            except discord.LoginFailure:
                bot_info_future.set_exception(Exception("Invalid BOT_TOKEN"))
            except Exception as e:
                bot_info_future.set_exception(e)

            return await bot_info_future

        # Run the asyncio logic inside the test
        try:
            bot_user = asyncio.run(run_bot_test())
            self.assertIsNotNone(bot_user, "Failed to get bot user")
            print(f"✅ Bot is authenticated as: {bot_user.name}#{bot_user.discriminator} (ID: {bot_user.id})")
        except Exception as e:
            self.fail(f"Discord bot test failed: {e}")

if __name__ == "__main__":
    unittest.main()

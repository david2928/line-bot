#!/usr/bin/env python3
"""
Simplified Inventory Update Script for GitHub Actions

This script reads a single cell from Google Sheets and sends its content to LINE groups.
"""

import os
import json
import requests
from google.oauth2 import service_account
import googleapiclient.discovery
from datetime import datetime

# Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_credentials():
    """Get Google service account credentials from environment variables"""
    print("Setting up Google credentials")
    
    creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not creds_json:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable is not set")
    
    try:
        # Try parsing as JSON
        creds_info = json.loads(creds_json)
        return service_account.Credentials.from_service_account_info(
            creds_info, scopes=SCOPES)
    except json.JSONDecodeError:
        # If it's not valid JSON, it might be escaped or in a different format
        print("Warning: Credentials not in valid JSON format, attempting to fix")
        
        # Try removing quotes if they wrap the entire string
        if creds_json.startswith('"') and creds_json.endswith('"'):
            creds_json = creds_json[1:-1]
        
        # Replace escaped quotes
        creds_json = creds_json.replace('\\"', '"')
        
        try:
            creds_info = json.loads(creds_json)
            return service_account.Credentials.from_service_account_info(
                creds_info, scopes=SCOPES)
        except json.JSONDecodeError as e:
            print(f"Error parsing credentials JSON: {e}")
            raise ValueError("Invalid Google credentials format")

def get_cell_content():
    """Fetch content of a single cell from Google Sheets"""
    print("Getting content from Google Sheets")
    
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')
    if not spreadsheet_id:
        raise ValueError("SPREADSHEET_ID environment variable is not set")
    
    sheet_name = os.environ.get('SHEET_NAME', 'Last Entry')
    cell = os.environ.get('START_CELL', 'B12')
    
    range_name = f"'{sheet_name}'!{cell}"
    print(f"Reading from {range_name}")
    
    credentials = get_credentials()
    service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("No data found in cell")
            return "No inventory data available"
        
        # Extract the single cell value
        cell_value = values[0][0] if values and values[0] else "No inventory data available"
        print(f"Cell content: {cell_value}")
        
        return cell_value
    except Exception as e:
        print(f"Error accessing sheet: {str(e)}")
        # Try to list available sheets to help with troubleshooting
        try:
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = spreadsheet.get('sheets', [])
            sheet_names = [sheet['properties']['title'] for sheet in sheets]
            print(f"Available sheets: {', '.join(sheet_names)}")
        except:
            pass
        raise

def format_message(cell_content):
    """Format the cell content into the specified message structure"""
    formatted_message = "🛒 Weekly Inventory Update 🛒\n\n"
    formatted_message += "This week's inventory status:\n\n"
    formatted_message += "Items to be re-ordered: \n"
    formatted_message += cell_content
    formatted_message += "\n\nPlease proceed with the necessary orders."
    
    return formatted_message

def send_line_message(message):
    """Send message to LINE groups"""
    print("Sending message to LINE groups")
    
    channel_token = os.environ.get('CHANNEL_ACCESS_TOKEN')
    if not channel_token:
        raise ValueError("CHANNEL_ACCESS_TOKEN environment variable is not set")
    
    group_ids_str = os.environ.get('LINE_GROUP_IDS')
    if not group_ids_str:
        raise ValueError("LINE_GROUP_IDS environment variable is not set")
    
    group_ids = group_ids_str.split(',')
    print(f"Sending to {len(group_ids)} LINE group(s)")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {channel_token}'
    }
    
    for group_id in group_ids:
        group_id = group_id.strip()
        if not group_id:
            continue
            
        payload = {
            'to': group_id,
            'messages': [
                {
                    'type': 'text',
                    'text': message
                }
            ]
        }
        
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        print(f"Message sent to group {group_id}")

def main():
    """Main function to run the inventory update"""
    try:
        print(f"Starting inventory update process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get cell content from Google Sheets
        cell_content = get_cell_content()
        
        # Format the message
        message = format_message(cell_content)
        
        # Send the message to LINE groups
        send_line_message(message)
        
        print("Inventory update completed successfully")
        return True
    except Exception as e:
        print(f"Error during inventory update: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
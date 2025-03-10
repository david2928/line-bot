#!/usr/bin/env python3
"""
Inventory Update Script for GitHub Actions

This script connects to the LINE API and Google Sheets to generate 
and send inventory updates to configured LINE groups.
"""

import os
import json
import requests
from google.oauth2 import service_account
import googleapiclient.discovery
from datetime import datetime

# Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_inventory_data():
    """Fetch inventory data from Google Sheets"""
    print("Getting inventory data from Google Sheets")
    
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')
    if not spreadsheet_id:
        raise ValueError("SPREADSHEET_ID environment variable is not set")
    
    # Load credentials from the environment variable file path
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not creds_path or not os.path.exists(creds_path):
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set or file doesn't exist")
    
    credentials = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES)
    
    # Create Google Sheets API service
    service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
    
    # Fetch data from the inventory sheet
    range_name = 'Inventory!A2:E'  # Adjust based on your sheet structure
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    
    rows = result.get('values', [])
    
    if not rows:
        print("No data found in the sheet")
        return []
    
    # Process the data to identify items that need to be reordered
    reorder_items = []
    for row in rows:
        # Skip rows with insufficient data
        if len(row) < 3:
            continue
            
        # Assuming column structure: Item, Current Quantity, Reorder Level
        item = row[0]
        try:
            current_qty = int(row[1]) if row[1] else 0
            reorder_level = int(row[2]) if len(row) > 2 and row[2] else 0
        except ValueError:
            # Skip rows with non-numeric quantity/reorder level
            continue
            
        if current_qty <= reorder_level:
            reorder_items.append({
                'item': item,
                'current_qty': current_qty,
                'reorder_level': reorder_level
            })
    
    print(f"Found {len(reorder_items)} items that need to be reordered")
    return reorder_items

def format_inventory_message(reorder_items):
    """Format the inventory data into a LINE message"""
    print("Formatting inventory message")
    
    if not reorder_items:
        return "✅ No items need to be reordered this week."
    
    message = "🚨 INVENTORY REORDER ALERT 🚨\n\n"
    message += "The following items need to be reordered:\n\n"
    
    for item in reorder_items:
        message += f"• {item['item']}: {item['current_qty']} remaining (Reorder at {item['reorder_level']})\n"
    
    return message

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
    print(f"Found {len(group_ids)} LINE group(s) to message")
    
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
        
        # Get inventory data from Google Sheets
        reorder_items = get_inventory_data()
        
        # Format the message
        message = format_inventory_message(reorder_items)
        
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
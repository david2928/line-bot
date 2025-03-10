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
            # If still failing, provide more detailed error
            print(f"Error parsing credentials JSON: {e}")
            print(f"First 20 characters of credentials: {creds_json[:20]}...")
            raise ValueError("Invalid Google credentials format. Please ensure it's a valid JSON service account key")

def get_sheet_info():
    """Get sheet name and range from environment variables or use defaults"""
    # Get sheet name from environment variable or use default
    sheet_name = os.environ.get('SHEET_NAME', 'Last Entry')
    print(f"Using sheet: '{sheet_name}'")
    
    # Get start cell from environment variable or use default
    start_cell = os.environ.get('START_CELL', 'B12')
    
    # If end_cell is provided, make a range, otherwise use just the start_cell
    end_cell = os.environ.get('END_CELL')
    
    if end_cell:
        # If it's just a column letter (like 'D'), append row from start_cell
        if end_cell.isalpha():
            # Extract row number from start_cell
            row_num = ''.join(filter(str.isdigit, start_cell))
            if row_num:
                end_cell = f"{end_cell}{row_num}"
            range_str = f"'{sheet_name}'!{start_cell}:{end_cell}"
        else:
            range_str = f"'{sheet_name}'!{start_cell}:{end_cell}"
    else:
        # Just use the single cell
        range_str = f"'{sheet_name}'!{start_cell}"
    
    print(f"Using range: {range_str}")
    return range_str

def list_all_sheets(service, spreadsheet_id):
    """List all available sheets in the spreadsheet"""
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get('sheets', [])
        
        print("Available sheets in this spreadsheet:")
        for sheet in sheets:
            print(f"- {sheet['properties']['title']}")
        
        return [sheet['properties']['title'] for sheet in sheets]
    except Exception as e:
        print(f"Error listing sheets: {str(e)}")
        return []

def get_inventory_data():
    """Fetch inventory data from Google Sheets"""
    print("Getting inventory data from Google Sheets")
    
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')
    if not spreadsheet_id:
        raise ValueError("SPREADSHEET_ID environment variable is not set")
    
    credentials = get_credentials()
    
    # Create Google Sheets API service
    service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
    
    # First, list all available sheets to help with troubleshooting
    available_sheets = list_all_sheets(service, spreadsheet_id)
    
    # Get the range to read
    range_name = get_sheet_info()
    
    try:
        # Fetch data from the sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        
        rows = result.get('values', [])
        
        if not rows:
            print("No data found in the sheet")
            return []
        
        # The structure will depend on whether we're dealing with a range or single cell
        # For simplicity in this example, we'll create a structure for reorder items
        # based on the data we find
        
        # If it's a single cell or single row
        if len(rows) == 1 and len(rows[0]) == 1:
            print(f"Found single cell value: {rows[0][0]}")
            # Assume this is a number representing items to reorder
            try:
                count = int(rows[0][0])
                return [{"item": "Inventory items", "current_qty": count, "reorder_level": 0}]
            except (ValueError, TypeError):
                # If it's not a number, just return it as a message
                return [{"item": rows[0][0], "current_qty": 0, "reorder_level": 0}]
        
        # Process the data to identify items that need to be reordered
        reorder_items = []
        for row in rows:
            # Skip empty rows
            if not row:
                continue
                
            # Handle different data formats based on column count
            if len(row) == 1:
                # Only one column - treat as item name
                reorder_items.append({
                    "item": row[0],
                    "current_qty": 0,
                    "reorder_level": 0
                })
            elif len(row) >= 3:
                # Assuming column structure: Item, Current Quantity, Reorder Level
                item = row[0]
                try:
                    current_qty = int(row[1]) if row[1] else 0
                    reorder_level = int(row[2]) if len(row) > 2 and row[2] else 0
                except ValueError:
                    # Skip rows with non-numeric quantity/reorder level
                    current_qty = 0
                    reorder_level = 0
                    
                reorder_items.append({
                    "item": item,
                    "current_qty": current_qty,
                    "reorder_level": reorder_level
                })
            elif len(row) == 2:
                # Just item and quantity
                item = row[0]
                try:
                    current_qty = int(row[1]) if row[1] else 0
                except ValueError:
                    current_qty = 0
                
                reorder_items.append({
                    "item": item,
                    "current_qty": current_qty,
                    "reorder_level": 0
                })
        
        print(f"Found {len(reorder_items)} items that need to be reordered")
        print(f"Data preview: {reorder_items[:2]}")
        return reorder_items
    except Exception as e:
        print(f"Error accessing sheet: {str(e)}")
        print(f"Make sure the sheet name is correct and exists in the spreadsheet.")
        print(f"Available sheets: {', '.join(available_sheets)}")
        raise

def format_inventory_message(reorder_items):
    """Format the inventory data into a LINE message"""
    print("Formatting inventory message")
    
    if not reorder_items:
        return "✅ No items need to be reordered this week."
    
    # If we're working with raw data from a cell, just return it directly
    if len(reorder_items) == 1 and not reorder_items[0].get("current_qty") and not reorder_items[0].get("reorder_level"):
        return reorder_items[0]["item"]
    
    message = "🚨 INVENTORY REORDER ALERT 🚨\n\n"
    message += "The following items need to be reordered:\n\n"
    
    for item in reorder_items:
        # If there's a reorder level, include it
        if item.get("reorder_level"):
            message += f"• {item['item']}: {item['current_qty']} remaining (Reorder at {item['reorder_level']})\n"
        else:
            message += f"• {item['item']}: {item['current_qty']} remaining\n"
    
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
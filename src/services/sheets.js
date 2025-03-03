const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

/**
 * Function to authenticate with Google Sheets API
 * You'll need to set up service account credentials and add them to your .env file
 * See: https://cloud.google.com/docs/authentication/getting-started
 */
async function getAuthClient() {
  try {
    // If using environment variables that contain JSON
    if (process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON) {
      let credentials;
      const credentialsValue = process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON;
      
      // Check if it's a file path or JSON content
      if (credentialsValue.endsWith('.json') && !credentialsValue.startsWith('{')) {
        console.log(`Reading credentials from file: ${credentialsValue}`);
        try {
          // Try to read as relative path
          const filePath = path.resolve(process.cwd(), credentialsValue);
          credentials = JSON.parse(fs.readFileSync(filePath, 'utf8'));
          console.log('Successfully loaded credentials from file');
        } catch (fileError) {
          console.error('Error loading credentials file:', fileError);
          throw new Error(`Could not read credentials file: ${credentialsValue}`);
        }
      } else {
        // Try to parse as JSON string
        try {
          credentials = JSON.parse(credentialsValue);
          console.log('Using credentials from environment variable JSON');
        } catch (jsonError) {
          console.error('Error parsing credentials JSON:', jsonError);
          throw new Error('Invalid JSON in GOOGLE_APPLICATION_CREDENTIALS_JSON');
        }
      }
      
      const client = new google.auth.JWT(
        credentials.client_email,
        null,
        credentials.private_key,
        ['https://www.googleapis.com/auth/spreadsheets.readonly']
      );
      await client.authorize();
      return client;
    } 
    
    // If using a credentials file path in GOOGLE_APPLICATION_CREDENTIALS
    if (process.env.GOOGLE_APPLICATION_CREDENTIALS) {
      console.log(`Using credentials file from GOOGLE_APPLICATION_CREDENTIALS: ${process.env.GOOGLE_APPLICATION_CREDENTIALS}`);
      return new google.auth.GoogleAuth({
        keyFile: process.env.GOOGLE_APPLICATION_CREDENTIALS,
        scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
      });
    }

    throw new Error('No Google credentials provided');
  } catch (error) {
    console.error('Error authenticating with Google:', error);
    throw error;
  }
}

/**
 * Get inventory data from Google Sheets
 */
async function getInventoryData() {
  try {
    const auth = await getAuthClient();
    const sheets = google.sheets({ version: 'v4', auth });
    
    const spreadsheetId = process.env.SPREADSHEET_ID;
    const sheetName = process.env.SHEET_NAME || 'Last Entry';
    const range = process.env.SHEET_RANGE || 'B12';

    const response = await sheets.spreadsheets.values.get({
      spreadsheetId,
      range: `${sheetName}!${range}`,
    });

    return response.data.values[0][0];
  } catch (error) {
    console.error('Error fetching data from sheets:', error);
    throw error;
  }
}

/**
 * Format the inventory update message
 */
function formatInventoryMessage(reorderItems) {
  return '\n🛒 *Weekly Inventory Update* 🛒\n\n' + 
         'This week\'s inventory status:\n\n' + 
         '*Items to be re-ordered:* ' + reorderItems + 
         '\n\nPlease proceed with the necessary orders.';
}

module.exports = {
  getInventoryData,
  formatInventoryMessage
}; 
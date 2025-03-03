# LINE Bot for Inventory Updates

A Node.js application that integrates with LINE messaging API and Google Sheets to manage and update inventory information.

## Features

- Webhook endpoint for LINE messages
- Inventory update functionality via Google Sheets
- Notification system for inventory changes
- Authentication with Google API

## Requirements

- Node.js 14+
- LINE Messaging API channel
- Google Cloud account with Google Sheets API enabled
- Google Cloud service account with appropriate permissions

## Environment Variables

The application requires the following environment variables:

```
CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
CHANNEL_SECRET=your_line_channel_secret
SPREADSHEET_ID=your_google_spreadsheet_id
LINE_GROUP_IDS=comma_separated_line_group_ids
GOOGLE_APPLICATION_CREDENTIALS=path_to_credentials_file
```

## Local Development

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables in a `.env` file
4. Start the server: `node src/app.js`

## Deployment

### Manual Deployment to Google Cloud Run

```bash
# Build the container
docker build -t gcr.io/[PROJECT_ID]/line-bot .

# Push to Container Registry
docker push gcr.io/[PROJECT_ID]/line-bot

# Deploy to Cloud Run
gcloud run deploy line-bot \
  --image gcr.io/[PROJECT_ID]/line-bot \
  --platform managed \
  --region [REGION] \
  --allow-unauthenticated \
  --set-env-vars="CHANNEL_ACCESS_TOKEN=[VALUE],CHANNEL_SECRET=[VALUE],SPREADSHEET_ID=[VALUE],LINE_GROUP_IDS=[VALUE]" \
  --service-account="[SERVICE_ACCOUNT_EMAIL]"
```

### Automated Deployment with GitHub Actions

This repository includes a GitHub Actions workflow file that automatically deploys the application to Google Cloud Run when changes are pushed to the main branch.

To set up automated deployment:

1. Fork or clone this repository to your GitHub account
2. Set up the following secrets in your GitHub repository settings:
   - `GCP_SA_KEY`: The JSON key of your Google Cloud service account
   - `CHANNEL_ACCESS_TOKEN`: Your LINE channel access token
   - `CHANNEL_SECRET`: Your LINE channel secret
   - `SPREADSHEET_ID`: Your Google Spreadsheet ID
   - `LINE_GROUP_IDS`: Comma-separated LINE group IDs
3. Push changes to the main branch to trigger deployment

## Accessing the Application

After deployment, your application will be available at the URL provided by Google Cloud Run.

## Webhook Configuration

Configure your LINE Messaging API channel to use the deployed URL as the webhook URL:

```
https://[YOUR_CLOUD_RUN_URL]/webhook
```

## Features

- Fetches inventory data from Google Sheets
- Formats and sends weekly inventory updates via LINE Messaging API
- Provides both scheduled and manual update triggers
- Simple Express API for management

## Setup Instructions

### Prerequisites

- Node.js v14+ installed
- A LINE Bot with Messaging API enabled
- Google Sheets API credentials
- A Google Spreadsheet with inventory data

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   npm install
   ```
3. Copy `.env.example` to `.env` and configure your environment variables:
   ```
   cp .env.example .env
   ```

### Configuration

In your `.env` file, set the following variables:

- `CHANNEL_ACCESS_TOKEN`: Your LINE Messaging API channel access token
- `CHANNEL_SECRET`: Your LINE channel secret
- `SPREADSHEET_ID`: The ID of your Google Spreadsheet
- `SHEET_NAME`: The name of the sheet containing inventory data (default: "Last Entry")
- `SHEET_RANGE`: The cell range to read (default: "B12")
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`: Your Google service account credentials as a JSON string
  - Alternatively, set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your credentials file
- `LINE_GROUP_IDS`: Comma-separated list of LINE group IDs to send messages to
- `AUTO_START_SCHEDULER`: Set to "true" to automatically start the weekly scheduler on server start

### Getting LINE Group IDs

You can obtain the LINE group ID by:

1. Adding your bot to the target group
2. Having a group member send the message "!id" in the group
3. The bot will reply with the group ID which you can then add to your `.env` file

## Usage

### Starting the Server

```
npm start
```

For development with auto-restart:
```
npm run dev
```

### API Endpoints

- `POST /inventory/update`: Manually trigger an inventory update
- `POST /inventory/schedule/start`: Start the weekly inventory scheduler
- `POST /inventory/schedule/stop`: Stop the weekly inventory scheduler
- `GET /status`: Check server status
- `POST /test/message`: Test sending a message to a group
  - Request body: `{ "groupId": "your-group-id", "message": "Your test message" }`

## Deployment

This application can be deployed to any Node.js hosting platform such as:

- Vercel
- Google Cloud Run
- Heroku
- AWS Lambda
- Azure Functions

For production use, consider using a proper job scheduler service like Google Cloud Scheduler to trigger the inventory update endpoint rather than relying on the in-memory scheduler.

## Troubleshooting

### Bot Not Responding to Commands

If your bot is not responding to commands like `!id` in a group, check the following:

1. **Webhook URL Configuration**:
   - In the LINE Developer Console, verify your webhook URL is correctly set
   - Format: `https://your-domain.com/webhook`
   - Ensure the webhook status shows as "Verified"

2. **Bot Permissions**:
   - Check that your bot has the following permissions enabled:
     - "Use webhook"
     - "Message sending"
     - "Use reply message"
     - Optional: "Chat history" and "Groups"

3. **Webhook Events**:
   - Ensure you've subscribed to the appropriate webhook events:
     - "Join" events
     - "Message" events
     - "MemberJoined" events (if needed)

4. **Server Logs**:
   - Check your server logs to see if webhook events are being received
   - If events are received but the bot doesn't respond, check for errors in the logs

5. **Testing the API**:
   - Use the `/test/message` endpoint to send a test message
   - Use the `/test/getId` endpoint to test getting a group ID

### Getting Group/Room IDs

If the `!id` command isn't working, you can try these alternatives:

1. **Using the Test Endpoint**:
   - If you know any group ID, use the `/test/getId` endpoint to send an ID message
   - Example POST request: `{ "groupId": "C1234567890abcdef" }`

2. **Check Server Logs**:
   - When a message is sent in a group, the server logs should show the group ID
   - Look for logs containing `Source type: group, ID: ...`

3. **Manual Testing**:
   - Add console.log statements to the webhook handler
   - Deploy and check the logs when messages are sent

## Migrating from LINE Notify

This application replaces the functionality of LINE Notify, which is being discontinued on March 31, 2025. The key differences are:

1. LINE Notify sent messages as a notification bot
2. LINE Messaging API sends messages as your LINE Official Account
3. Users need to add your bot to groups to receive messages
4. You need to obtain group IDs instead of using a Notify token

## Local Development

### Testing with ngrok

To test the bot locally, you'll need to make your local server accessible to LINE's servers. You can do this using ngrok:

1. **Install ngrok**:
   ```bash
   npm install -g ngrok
   # or download from https://ngrok.com/download
   ```

2. **Start your local server**:
   ```bash
   npm run dev
   ```

3. **Start ngrok** (in a new terminal):
   ```bash
   ngrok http 3000
   ```

4. **Configure LINE Developer Console**:
   - Copy the https URL from ngrok (e.g., `https://xxxx-xx-xx-xx-xx.ngrok.io`)
   - Go to your LINE Developer Console
   - Set the Webhook URL to: `https://xxxx-xx-xx-xx-xx.ngrok.io/webhook`
   - Click "Verify" to test the connection

5. **Test the bot**:
   - Send `!help` in your LINE group to see available commands
   - Send `!id` to get the group ID
   - Check your terminal for webhook logs

### Important Notes for Local Testing

1. **Ngrok URL Changes**:
   - Each time you restart ngrok, you'll get a new URL
   - You'll need to update the webhook URL in LINE Developer Console
   - Consider getting a fixed ngrok URL with a paid plan for longer development sessions

2. **Debugging**:
   - Check the terminal running your Express server for logs
   - The ngrok web interface (usually at http://127.0.0.1:4040) shows all webhook requests
   - Use the test endpoints to verify functionality:
     ```bash
     # Test if server is running
     curl http://localhost:3000/status
     
     # Test sending a message (replace GROUP_ID)
     curl -X POST http://localhost:3000/test/message \
       -H "Content-Type: application/json" \
       -d '{"groupId":"GROUP_ID","message":"Test message"}'
     ```

## License

MIT 
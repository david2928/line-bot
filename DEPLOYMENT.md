# Deploying to Google Cloud Run

This guide explains how to deploy the LINE Inventory Bot to Google Cloud Run using GitHub Actions CI/CD.

## Prerequisites

1. A Google Cloud Project
2. A GitHub repository for your code
3. Google Cloud billing enabled
4. Required Google Cloud APIs enabled:
   - Cloud Run API
   - Container Registry API
   - Secret Manager API

## Setup Steps

### 1. Create a Service Account

1. Go to the [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) page
2. Click "Create Service Account"
3. Name it "github-actions-deployer" or similar
4. Grant the following roles:
   - Cloud Run Admin
   - Storage Admin
   - Secret Manager Admin
   - Service Account User

### 2. Create a Service Account Key

1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose JSON format
5. Download the key file

### 3. Set up GitHub Secrets

Add the following secrets to your GitHub repository:

1. `GCP_PROJECT_ID`: Your Google Cloud project ID
2. `GCP_SA_KEY`: The entire contents of the service account key JSON file

### 4. Store Sensitive Configuration in Secret Manager

Create the following secrets in Google Cloud Secret Manager:

1. `CHANNEL_ACCESS_TOKEN`: Your LINE Channel Access Token
2. `CHANNEL_SECRET`: Your LINE Channel Secret
3. `SPREADSHEET_ID`: Your Google Sheets spreadsheet ID
4. `GOOGLE_APPLICATION_CREDENTIALS_JSON`: The service account key JSON for accessing Google Sheets
5. `LINE_GROUP_IDS`: Comma-separated list of LINE group IDs

```bash
# Example commands to create secrets
echo -n "your-line-channel-access-token" | \
  gcloud secrets create CHANNEL_ACCESS_TOKEN --data-file=-

echo -n "your-line-channel-secret" | \
  gcloud secrets create CHANNEL_SECRET --data-file=-

echo -n "your-spreadsheet-id" | \
  gcloud secrets create SPREADSHEET_ID --data-file=-

# For the Google credentials, use the path to your JSON file
gcloud secrets create GOOGLE_APPLICATION_CREDENTIALS_JSON --data-file=/path/to/google-credentials.json

echo -n "group-id-1,group-id-2" | \
  gcloud secrets create LINE_GROUP_IDS --data-file=-
```

### 5. Deploy the Application

After setting up the GitHub repository with the workflow file:

1. Push your code to the main branch
2. The GitHub Actions workflow will automatically build and deploy your application
3. Alternatively, go to the "Actions" tab in your GitHub repository and manually trigger the workflow

### 6. Configure LINE Webhook URL

After deployment:

1. Get the Cloud Run service URL from the GitHub Actions output
2. Set your LINE Bot webhook URL to: `https://your-cloud-run-url.run.app/webhook`
3. Verify the webhook in the LINE Developer Console

## Monitoring and Maintenance

- View logs in the Google Cloud Console under Cloud Run > Services > line-inventory-bot > Logs
- Set up Google Cloud Monitoring for alerts on errors or performance issues
- Update your code by pushing to the main branch; GitHub Actions will handle deployment

## Scheduling Inventory Updates

For reliable scheduling, set up Google Cloud Scheduler:

1. Go to Cloud Scheduler in the Google Cloud Console
2. Create a new job that calls your `/inventory/update` endpoint weekly
3. Use the following settings:
   - Frequency: `0 0 * * 1` (Every Monday at midnight)
   - Target: HTTP
   - URL: `https://your-cloud-run-url.run.app/inventory/update`
   - HTTP Method: POST
   - Auth header: None (if your endpoint is public)

This is more reliable than the in-memory scheduler in the application. 
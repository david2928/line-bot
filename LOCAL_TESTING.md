# Local Testing Instructions for Inventory Update Workflow

## Option 1: Test the Curl Command Directly

You can test the core functionality of the GitHub Actions workflow by running the curl command locally:

```bash
# 1. Authenticate with Google Cloud
gcloud auth login

# 2. Get an identity token for your Cloud Run service
TOKEN=$(gcloud auth print-identity-token --audiences=https://line-inventory-bot-chxb6w667a-an.a.run.app/inventory/update)

# 3. Send the request to your endpoint
curl -X POST "https://line-inventory-bot-chxb6w667a-an.a.run.app/inventory/update" \
  -H "Authorization: Bearer $TOKEN"
```

## Option 2: Use GitHub Actions Local Runner (Act)

You can use [Act](https://github.com/nektos/act) to run GitHub Actions workflows locally:

1. Install Act:
   - On Windows with Chocolatey: `choco install act-cli`
   - On macOS with Homebrew: `brew install act`
   - On Linux: Check the [Act GitHub page](https://github.com/nektos/act) for installation instructions

2. Create a `.secrets` file in your project root with your GCP credentials:
   ```
   GCP_SA_KEY=<<Your GCP service account key JSON>>
   ```

3. Run the workflow with Act:
   ```bash
   act workflow_dispatch -j trigger-inventory-update --secret-file .secrets
   ```

   Note: The `workflow_dispatch` event triggers the workflow manually.

4. Important considerations for Act:
   - Act runs workflows in Docker containers
   - Some Google Cloud authentication may behave differently in the container environment
   - You might need to modify the workflow slightly for local testing

## Option 3: Test the Endpoint Directly

You can also test the endpoint directly using tools like Postman or Insomnia:

1. Set up a new request in Postman:
   - Method: POST
   - URL: https://line-inventory-bot-chxb6w667a-an.a.run.app/inventory/update
   - Headers:
     - Authorization: Bearer [your-token]

2. Get the token using the Google Cloud CLI:
   ```bash
   gcloud auth print-identity-token --audiences=https://line-inventory-bot-chxb6w667a-an.a.run.app/inventory/update
   ```

3. Copy the token and paste it into the Authorization header in Postman

4. Send the request and check the response

## Option 4: Manual Trigger in GitHub

Once the workflow is pushed to GitHub, you can manually trigger it:

1. Go to the "Actions" tab in your GitHub repository
2. Click on "Weekly Inventory Update" workflow
3. Click "Run workflow" dropdown
4. Click "Run workflow" button

This will run the entire workflow, just as if it were triggered by the schedule.

## Troubleshooting

If you encounter authentication issues:
- Ensure your service account has the appropriate permissions
- Check that the audience URL matches exactly with your Cloud Run service
- Verify that the service account key is correctly formatted in your secrets 
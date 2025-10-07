This guide walks you through every step—from creating a Google Cloud project and OAuth app to packaging your Python script—so a beginner can generate their own credentials.json, add test users, and publish a reusable package.

Prerequisites: Python 3.7+, Google account

1. Create a Google Cloud Project
Open the Cloud Console at https://console.cloud.google.com

Click the project drop-down in the top bar and select New Project.

Enter a Project name (e.g., “Gmail Automation”), choose your organization if prompted, and click Create.

Wait for the project creation notification and ensure Gmail Automation is selected.

2. Enable the Gmail API
In the left sidebar, go to APIs & Services > Library.

Search for Gmail API and click it.

Click Enable. If it already shows “Enabled,” click Manage, then Disable API, wait a few seconds, and Enable again.

3. Configure the OAuth Consent Screen
Still under APIs & Services, click OAuth consent screen.

Select External (so any Google user can test) and click Create.

Fill in:

App name: “Gmail Cleanup Script”

User support email: your email

Developer email address: your email

Click Save and Continue past Scopes and Summary (you’ll add test users next).

4. Add Yourself as a Test User
On the OAuth consent screen page, scroll down to Test users.

Click Add users, enter your Gmail address (e.g., youremail@gmail.com), and click Add.

Click Save and Continue if prompted.

Why?
When an app is “in testing,” only listed test users can authorize it. This lets you proceed without full Google verification.

5. Create OAuth 2.0 Credentials
Navigate to APIs & Services > Credentials.

Click Create Credentials > OAuth client ID.

For Application type, choose Desktop app.

Name it (e.g., “Gmail CLI”), then click Create.

In the dialog that appears, click Download JSON. This file is your credentials.json


Installation:

git clone https://github.com/yourusername/gmail-cleanup.git
cd gmail-cleanup
python3 -m venv .venv
source .venv/bin/activate
cp credentials.example.json credentials.json
# Edit credentials.json with your OAuth details
pip install .

Note : Copy this file to credentials.example. json to credentials.json(use this one) and replace placeholders

Usage:

pip install gmail-cleanup

Notes: Test user, Gmail API enablement, token file location.
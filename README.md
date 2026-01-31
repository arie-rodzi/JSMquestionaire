# Streamlit Questionnaire → Google Sheets

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Secrets
Create `.streamlit/secrets.toml` (do not commit) and paste your Google service account credentials.

Example:
```toml
[gcp_service_account]
type = "service_account"
project_id = "PROJECT_ID"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "xxxx@xxxx.iam.gserviceaccount.com"
token_uri = "https://oauth2.googleapis.com/token"

[app]
spreadsheet_name = "YOUR_SHEET_NAME"
worksheet_name = "responses"
```

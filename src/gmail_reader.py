from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[1]

CREDENTIALS_FILE = ROOT / "credentials.json"
TOKEN_FILE = ROOT / "token.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

DIT_EMAIL = "info.defineinfotech@gmail.com"


def connect_gmail():
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE), SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    "credentials.json file not found."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_task_emails():
    service = connect_gmail()

    query = f"from:{DIT_EMAIL} newer_than:30d"

    result = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=50
    ).execute()

    emails = []

    for message in result.get("messages", []):
        mail = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()

        headers = mail.get("payload", {}).get("headers", [])

        details = {
            item["name"].lower(): item["value"]
            for item in headers
        }

        emails.append({
            "Message ID": message["id"],
            "Subject": details.get("subject", ""),
            "From": details.get("from", ""),
            "Date": details.get("date", ""),
            "Preview": mail.get("snippet", "")
        })

    return emails
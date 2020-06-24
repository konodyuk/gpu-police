import pickle
import os.path
import sys
import collections
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pathlib import Path

from gpu_police.config import config

SCOPES = config.whitelist.scopes
SPREADSHEET_ID = config.whitelist.spreadsheet_id

def update_token():
    creds_file = Path(config.whitelist.credentials).expanduser()
    flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
    creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

def _get_values(query):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        else:
            update_token()

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=query).execute()
    names = result.get('values', [])

    return names

def get_whitelist():
    result = []
    for query in config.whitelist.queries:
        result += _get_values(query)
    result = [i[0] for i in result if i]

    return result

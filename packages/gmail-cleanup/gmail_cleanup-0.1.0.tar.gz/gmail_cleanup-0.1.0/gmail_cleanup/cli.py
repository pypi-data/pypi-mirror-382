# # 

# import os
# import pickle
# import time
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

# SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
# CREDENTIALS_FILE = 'credentials.json'
# TOKEN_FILE = 'token.pickle'
# QUERY = 'is:unread'
# MAX_RESULTS = 100  # Safer to start with 100; you can increase after testing

# def get_credentials():
#     creds = None
#     if os.path.exists(TOKEN_FILE):
#         with open(TOKEN_FILE, 'rb') as token:
#             creds = pickle.load(token)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open(TOKEN_FILE, 'wb') as token:
#             pickle.dump(creds, token)
#     return creds

# def trash_thread(service, thread_id):
#     # Robust deletion with retry
#     for i in range(5):
#         try:
#             service.users().threads().trash(userId='me', id=thread_id).execute()
#             return True
#         except HttpError as e:
#             print(f"Error deleting {thread_id}: {str(e)} — retrying...")
#             time.sleep(2**i)
#     return False

# def main():
#     creds = get_credentials()
#     service = build('gmail', 'v1', credentials=creds)
#     total_deleted = 0
#     page_token = None
#     page = 1

#     while True:
#         result = service.users().threads().list(
#             userId='me',
#             q=QUERY,
#             maxResults=MAX_RESULTS,
#             pageToken=page_token
#         ).execute()
#         threads = result.get('threads', [])
#         print(f"Page {page}: {len(threads)} unread threads found")

#         if not threads:
#             break

#         for idx, t in enumerate(threads, 1):
#             ok = trash_thread(service, t['id'])
#             msg = f"Thread {idx}/{len(threads)} - {'Deleted' if ok else 'FAILED'}"
#             print(msg)
#             if ok:
#                 total_deleted += 1

#         print(f"Page {page}: Deleted so far: {total_deleted}")
#         page_token = result.get('nextPageToken')
#         page += 1
#         if not page_token:
#             break

#     print(f"FINISHED: {total_deleted} unread threads moved to Trash.")

# if __name__ == '__main__':
#     main()

import os
import pickle
import time
from tqdm import tqdm
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
QUERY = 'is:unread'
MAX_RESULTS = 500

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def trash_thread(service, thread_id):
    for i in range(3):  # Retry quickly for robust deletion
        try:
            service.users().threads().trash(userId='me', id=thread_id).execute()
            return True
        except HttpError:
            time.sleep(2 ** i)
    return False

def cli_main():
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    total_deleted = 0
    page_token = None

    while True:
        result = service.users().threads().list(
            userId='me',
            q=QUERY,
            maxResults=MAX_RESULTS,
            pageToken=page_token
        ).execute()
        threads = result.get('threads', [])

        if not threads:
            break

        # Progress bar for current page
        for t in tqdm(threads, desc="Deleting unread emails"):
            if trash_thread(service, t['id']):
                total_deleted += 1

        page_token = result.get('nextPageToken')
        if not page_token:
            break

    print(f"\nFINISHED: {total_deleted} unread threads moved to Trash.")

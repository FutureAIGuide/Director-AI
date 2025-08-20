"""
cloud_storage.py

Provides Google Drive integration for Director-AI.
Allows uploading files to Google Drive and generating shareable links.
"""

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from typing import Optional

class GoogleDriveManager:
    def __init__(self, service_account_file: str):
        scopes = ['https://www.googleapis.com/auth/drive.file']
        self.creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        self.service = build('drive', 'v3', credentials=self.creds)

    def upload_file(self, file_path: str, folder_id: Optional[str] = None) -> Optional[str]:
        file_metadata = {'name': file_path.split('/')[-1]}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def get_shareable_link(self, file_id: str) -> str:
        self.service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
        ).execute()
        file = self.service.files().get(fileId=file_id, fields='webViewLink').execute()
        return file.get('webViewLink')

# Example usage:
# drive = GoogleDriveManager('path/to/service_account.json')
# file_id = drive.upload_file('results.csv')
# link = drive.get_shareable_link(file_id)
# print('Shareable link:', link)

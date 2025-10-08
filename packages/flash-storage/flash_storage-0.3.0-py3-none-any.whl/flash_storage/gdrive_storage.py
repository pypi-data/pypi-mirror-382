"""Google Drive storage operations for Git LFS."""

import os
import io
import webbrowser
from pathlib import Path
from typing import Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from .config import CloudinaryConfig
from .lfs_pointer import LFSPointer


class GoogleDriveStorage:
    """Handles upload and download operations with Google Drive."""

    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self, config: Optional[CloudinaryConfig] = None):
        """
        Initialize Google Drive storage.

        Args:
            config: CloudinaryConfig instance (creates new if None)
        """
        self.config = config or CloudinaryConfig()
        self.service = None
        self.folder_id = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Google Drive using OAuth 2.0."""
        creds = None

        # Check if we have a valid token
        token_data = self.config.get_gdrive_token()
        if token_data:
            creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)

        # If credentials are invalid or don't exist, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # Run OAuth flow
                creds_data = self.config.get_gdrive_credentials()
                if not creds_data:
                    raise ValueError(
                        "Google Drive credentials not configured. "
                        "Run 'flash setup-gdrive' first."
                    )

                # Create OAuth flow
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": creds_data["client_id"],
                            "client_secret": creds_data["client_secret"],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["http://localhost"]
                        }
                    },
                    self.SCOPES
                )

                # Run local server for OAuth
                creds = flow.run_local_server(port=0, open_browser=True)

            # Save the credentials for next run
            self.config.save_gdrive_token({
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            })

        # Build the Drive service
        self.service = build('drive', 'v3', credentials=creds)

        # Get or create folder for LFS files
        creds_data = self.config.get_gdrive_credentials()
        if creds_data:
            self.folder_id = creds_data.get("folder_id", "root")
            if self.folder_id == "root":
                # Create a dedicated folder for git-lfs files
                self.folder_id = self._get_or_create_folder("git-lfs-files")

    def _get_or_create_folder(self, folder_name: str) -> str:
        """Get or create a folder in Google Drive."""
        try:
            # Search for existing folder
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            items = results.get('files', [])
            if items:
                return items[0]['id']

            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            print(f"✓ Created Google Drive folder: {folder_name}")
            return folder['id']

        except HttpError as e:
            raise RuntimeError(f"Failed to create folder: {e}")

    def check_quota(self) -> Dict[str, int]:
        """
        Check Google Drive storage quota.

        Returns:
            Dictionary with 'used', 'limit', and 'available' in bytes
        """
        try:
            about = self.service.about().get(fields="storageQuota").execute()
            quota = about.get('storageQuota', {})

            used = int(quota.get('usage', 0))
            limit = int(quota.get('limit', 0))
            available = limit - used if limit > 0 else float('inf')

            return {
                'used': used,
                'limit': limit,
                'available': available
            }
        except HttpError as e:
            raise RuntimeError(f"Failed to check quota: {e}")

    def is_quota_full(self, file_size: int) -> bool:
        """
        Check if uploading a file would exceed quota.

        Args:
            file_size: Size of file in bytes

        Returns:
            True if quota would be exceeded, False otherwise
        """
        quota = self.check_quota()
        return file_size > quota['available']

    def upload(self, file_path: Path, pointer: LFSPointer) -> str:
        """
        Upload file to Google Drive.

        Args:
            file_path: Path to the file to upload
            pointer: LFS pointer for the file

        Returns:
            Google Drive file ID

        Raises:
            RuntimeError: If upload fails or quota is exceeded
        """
        try:
            # Check if file already exists
            existing_id = self._find_file_by_oid(pointer.oid)
            if existing_id:
                print(f"✓ File already exists in Google Drive: {pointer.oid[:8]}")
                return existing_id

            # Check quota before upload
            if self.is_quota_full(pointer.size):
                raise RuntimeError(
                    "Google Drive storage quota exceeded. "
                    "Please free up space or upgrade your storage."
                )

            # Upload file
            file_metadata = {
                'name': pointer.oid,
                'parents': [self.folder_id],
                'description': f"Git LFS file - Size: {pointer.size} bytes"
            }

            media = MediaFileUpload(
                str(file_path),
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webContentLink'
            ).execute()

            print(f"✓ Uploaded to Google Drive: {pointer.oid[:8]}")
            return file['id']

        except HttpError as e:
            if e.resp.status == 403 and 'quota' in str(e).lower():
                raise RuntimeError("Google Drive storage quota exceeded")
            raise RuntimeError(f"Failed to upload to Google Drive: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to upload to Google Drive: {e}")

    def download(self, pointer: LFSPointer, output_path: Path) -> None:
        """
        Download file from Google Drive.

        Args:
            pointer: LFS pointer containing the OID
            output_path: Path where to save the downloaded file

        Raises:
            FileNotFoundError: If file not found in Google Drive
            RuntimeError: If download fails
        """
        try:
            # Find file by OID
            file_id = self._find_file_by_oid(pointer.oid)
            if not file_id:
                raise FileNotFoundError(
                    f"File not found in Google Drive: {pointer.oid}"
                )

            # Download file
            request = self.service.files().get_media(fileId=file_id)

            # Create parent directories if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Write to file
            with open(output_path, 'wb') as f:
                f.write(fh.getvalue())

            print(f"✓ Downloaded from Google Drive: {pointer.oid[:8]}")

        except HttpError as e:
            if e.resp.status == 404:
                raise FileNotFoundError(f"File not found: {pointer.oid}")
            raise RuntimeError(f"Failed to download from Google Drive: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to download from Google Drive: {e}")

    def delete(self, pointer: LFSPointer) -> None:
        """
        Delete file from Google Drive.

        Args:
            pointer: LFS pointer containing the OID

        Raises:
            FileNotFoundError: If file not found
        """
        try:
            file_id = self._find_file_by_oid(pointer.oid)
            if not file_id:
                raise FileNotFoundError(f"File not found: {pointer.oid}")

            self.service.files().delete(fileId=file_id).execute()
            print(f"✓ Deleted from Google Drive: {pointer.oid[:8]}")

        except HttpError as e:
            if e.resp.status == 404:
                raise FileNotFoundError(f"File not found: {pointer.oid}")
            raise RuntimeError(f"Failed to delete from Google Drive: {e}")

    def exists(self, pointer: LFSPointer) -> bool:
        """
        Check if file exists in Google Drive.

        Args:
            pointer: LFS pointer containing the OID

        Returns:
            True if file exists, False otherwise
        """
        return self._find_file_by_oid(pointer.oid) is not None

    def _find_file_by_oid(self, oid: str) -> Optional[str]:
        """
        Find file in Google Drive by OID.

        Args:
            oid: The file's OID

        Returns:
            File ID if found, None otherwise
        """
        try:
            results = self.service.files().list(
                q=f"name='{oid}' and '{self.folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()

            items = results.get('files', [])
            if items:
                return items[0]['id']
            return None

        except HttpError:
            return None

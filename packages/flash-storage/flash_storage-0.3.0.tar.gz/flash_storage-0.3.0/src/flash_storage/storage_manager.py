"""Manages storage operations with fallback support between Cloudinary and Google Drive."""

from pathlib import Path
from typing import Optional, Tuple
from .config import CloudinaryConfig
from .cloudinary_storage import CloudinaryStorage
from .gdrive_storage import GoogleDriveStorage
from .lfs_pointer import LFSPointer


class StorageQuotaError(Exception):
    """Raised when storage quota is exceeded."""
    pass


class StorageManager:
    """Manages file storage with automatic fallback between Cloudinary and Google Drive."""

    def __init__(self, config: Optional[CloudinaryConfig] = None):
        """
        Initialize storage manager.

        Args:
            config: CloudinaryConfig instance (creates new if None)
        """
        self.config = config or CloudinaryConfig()
        self.cloudinary = None
        self.gdrive = None

        # Initialize Cloudinary if configured
        if self.config.is_configured():
            self.cloudinary = CloudinaryStorage(self.config)

        # Initialize Google Drive if credentials are configured (OAuth will run on first upload)
        if self.config.has_gdrive_credentials():
            self.gdrive = GoogleDriveStorage(self.config)


    def upload_with_fallback(self, file_path: Path, pointer: LFSPointer) -> Tuple[str, str]:
        """
        Upload file with automatic fallback support.

        Uses primary storage first (default: Cloudinary), automatically falls back to secondary if full.

        Args:
            file_path: Path to the file to upload
            pointer: LFS pointer for the file

        Returns:
            Tuple of (storage_name, url_or_id)
            - storage_name: 'cloudinary' or 'gdrive'
            - url_or_id: Cloudinary URL or Google Drive file ID

        Raises:
            RuntimeError: If upload fails on all available storage options
        """
        # Get primary storage preference
        primary = self.config.get_primary_storage()

        # Determine primary and secondary storage
        if primary == 'cloudinary':
            primary_storage = self.cloudinary
            primary_name = 'cloudinary'
            secondary_storage = self.gdrive
            secondary_name = 'gdrive'
        else:  # primary == 'gdrive'
            primary_storage = self.gdrive
            primary_name = 'gdrive'
            secondary_storage = self.cloudinary
            secondary_name = 'cloudinary'

        # Try primary storage first
        if primary_storage:
            try:
                if primary_name == 'cloudinary':
                    url_or_id = primary_storage.upload(file_path, pointer)
                    return (primary_name, url_or_id)
                else:  # gdrive
                    # Check quota before upload
                    if not primary_storage.is_quota_full(pointer.size):
                        file_id = primary_storage.upload(file_path, pointer)
                        return (primary_name, file_id)
                    else:
                        # Google Drive is full, trigger fallback
                        raise RuntimeError("Google Drive storage quota exceeded")

            except RuntimeError as e:
                error_msg = str(e).lower()

                # Check if it's a quota/storage issue
                if 'quota' in error_msg or 'storage' in error_msg or 'limit' in error_msg:
                    # Primary storage is full, try secondary automatically
                    if secondary_storage:
                        print(f"⚠️  {primary_name.replace('gdrive', 'Google Drive').replace('cloudinary', 'Cloudinary')} storage is full")
                        print(f"📤 Automatically uploading to {secondary_name.replace('gdrive', 'Google Drive').replace('cloudinary', 'Cloudinary')}...")

                        try:
                            if secondary_name == 'cloudinary':
                                url_or_id = secondary_storage.upload(file_path, pointer)
                                return (secondary_name, url_or_id)
                            else:  # gdrive
                                # Check quota for secondary too
                                if not secondary_storage.is_quota_full(pointer.size):
                                    file_id = secondary_storage.upload(file_path, pointer)
                                    return (secondary_name, file_id)
                                else:
                                    raise StorageQuotaError(
                                        f"Both {primary_name} and {secondary_name} storage are full. Please free up space."
                                    )

                        except Exception as secondary_error:
                            raise RuntimeError(
                                f"Primary storage ({primary_name}) is full and fallback to {secondary_name} failed: {secondary_error}"
                            )
                    else:
                        # No secondary storage configured
                        secondary_display = "Google Drive" if secondary_name == "gdrive" else "Cloudinary"
                        raise StorageQuotaError(
                            f"{primary_name.replace('gdrive', 'Google Drive').replace('cloudinary', 'Cloudinary')} storage is full and {secondary_display} is not configured. "
                            f"Run 'flash setup-gdrive' or 'flash setup' to enable fallback storage."
                        )
                else:
                    # Not a quota issue, re-raise
                    raise

        # No primary storage available, try secondary
        elif secondary_storage:
            print(f"⚠️  Primary storage ({primary_name}) not configured, using {secondary_name}...")
            try:
                if secondary_name == 'cloudinary':
                    url_or_id = secondary_storage.upload(file_path, pointer)
                    return (secondary_name, url_or_id)
                else:  # gdrive
                    file_id = secondary_storage.upload(file_path, pointer)
                    return (secondary_name, file_id)
            except Exception as e:
                raise RuntimeError(f"Upload to {secondary_name} failed: {e}")

        # No storage available at all
        raise RuntimeError(
            "No storage backend configured. Run 'flash setup' or 'flash setup-gdrive' first."
        )

    def download(self, pointer: LFSPointer, output_path: Path, storage: Optional[str] = None) -> None:
        """
        Download file from storage.

        Args:
            pointer: LFS pointer containing the OID
            output_path: Path where to save the downloaded file
            storage: Optional storage hint ('cloudinary' or 'gdrive')
                    If None, will try both storages

        Raises:
            FileNotFoundError: If file not found in any storage
        """
        # If storage hint provided, try that first
        if storage == 'cloudinary' and self.cloudinary:
            try:
                self.cloudinary.download(pointer, output_path)
                return
            except FileNotFoundError:
                pass

        if storage == 'gdrive' and self.gdrive:
            try:
                self.gdrive.download(pointer, output_path)
                return
            except FileNotFoundError:
                pass

        # Try all available storages
        errors = []

        if self.cloudinary:
            try:
                self.cloudinary.download(pointer, output_path)
                return
            except FileNotFoundError as e:
                errors.append(f"Cloudinary: {e}")

        if self.gdrive:
            try:
                self.gdrive.download(pointer, output_path)
                return
            except FileNotFoundError as e:
                errors.append(f"Google Drive: {e}")

        # File not found in any storage
        raise FileNotFoundError(
            f"File not found in any configured storage: {pointer.oid}\n" +
            "\n".join(errors)
        )

    def exists(self, pointer: LFSPointer) -> Tuple[bool, Optional[str]]:
        """
        Check if file exists in any storage.

        Args:
            pointer: LFS pointer containing the OID

        Returns:
            Tuple of (exists, storage_name)
            - exists: True if file exists, False otherwise
            - storage_name: 'cloudinary', 'gdrive', or None
        """
        if self.cloudinary and self.cloudinary.exists(pointer):
            return (True, 'cloudinary')

        if self.gdrive and self.gdrive.exists(pointer):
            return (True, 'gdrive')

        return (False, None)

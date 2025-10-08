"""Cloudinary storage operations for Git LFS."""

import os
from pathlib import Path
from typing import Optional, Dict
import cloudinary
import cloudinary.uploader
import cloudinary.api
from .config import CloudinaryConfig
from .lfs_pointer import LFSPointer


class CloudinaryStorage:
    """Handles upload and download operations with Cloudinary."""

    def __init__(self, config: Optional[CloudinaryConfig] = None):
        """
        Initialize Cloudinary storage.

        Args:
            config: CloudinaryConfig instance (creates new if None)
        """
        self.config = config or CloudinaryConfig()
        self._configure_cloudinary()

    def _configure_cloudinary(self) -> None:
        """Configure Cloudinary SDK with credentials."""
        creds = self.config.get_credentials()
        cloudinary.config(
            cloud_name=creds["cloud_name"],
            api_key=creds["api_key"],
            api_secret=creds["api_secret"],
            secure=True
        )
        self.folder = creds["folder"]

    def upload(self, file_path: Path, pointer: LFSPointer) -> str:
        """
        Upload file to Cloudinary.

        Args:
            file_path: Path to the file to upload
            pointer: LFS pointer for the file

        Returns:
            Cloudinary URL of the uploaded file
        """
        # Use OID as public_id to avoid duplicates
        public_id = f"{self.folder}/{pointer.oid}"

        try:
            # Check if file already exists (try with extensions)
            extensions_to_try = ['', '.txt', '.bin', '.dat', '.png', '.jpg', '.jpeg', '.gif', '.mp4', '.pdf', '.zip']

            for ext in extensions_to_try:
                try:
                    test_public_id = public_id + ext
                    existing = cloudinary.api.resource(
                        test_public_id,
                        resource_type="raw"
                    )
                    print(f"✓ File already exists in Cloudinary: {pointer.oid[:8]}")
                    return existing['secure_url']
                except cloudinary.api.NotFound:
                    continue
            # File doesn't exist, proceed with upload

            # Upload file - use_filename=False prevents Cloudinary from appending file extension
            result = cloudinary.uploader.upload(
                str(file_path),
                public_id=public_id,
                resource_type="raw",
                overwrite=False,
                invalidate=True,
                use_filename=False,
                tags=[f"size:{pointer.size}", "git-lfs"]
            )

            print(f"✓ Uploaded to Cloudinary: {pointer.oid[:8]}")
            return result['secure_url']

        except Exception as e:
            raise RuntimeError(f"Failed to upload to Cloudinary: {e}")

    def download(self, pointer: LFSPointer, output_path: Path) -> None:
        """
        Download file from Cloudinary.

        Args:
            pointer: LFS pointer containing the OID
            output_path: Path where to save the downloaded file
        """
        import requests

        # Construct the public_id
        public_id = f"{self.folder}/{pointer.oid}"

        # Common file extensions to try (Cloudinary auto-adds these)
        extensions_to_try = ['', '.txt', '.bin', '.dat', '.png', '.jpg', '.jpeg', '.gif', '.mp4', '.pdf', '.zip']

        url = None
        for ext in extensions_to_try:
            try:
                # Try to get resource with extension
                test_public_id = public_id + ext
                resource = cloudinary.api.resource(
                    test_public_id,
                    resource_type="raw"
                )
                url = resource['secure_url']
                break  # Found it!
            except cloudinary.api.NotFound:
                continue  # Try next extension

        if not url:
            raise FileNotFoundError(
                f"File not found in Cloudinary: {pointer.oid}"
            )

        try:
            # Download file
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Create parent directories if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✓ Downloaded from Cloudinary: {pointer.oid[:8]}")

        except Exception as e:
            raise RuntimeError(f"Failed to download from Cloudinary: {e}")

    def delete(self, pointer: LFSPointer) -> None:
        """
        Delete file from Cloudinary.

        Args:
            pointer: LFS pointer containing the OID
        """
        public_id = f"{self.folder}/{pointer.oid}"

        # Common file extensions to try (Cloudinary auto-adds these)
        extensions_to_try = ['', '.txt', '.bin', '.dat', '.png', '.jpg', '.jpeg', '.gif', '.mp4', '.pdf', '.zip']

        deleted = False
        for ext in extensions_to_try:
            try:
                test_public_id = public_id + ext
                cloudinary.uploader.destroy(
                    test_public_id,
                    resource_type="raw",
                    invalidate=True
                )
                print(f"✓ Deleted from Cloudinary: {pointer.oid[:8]}")
                deleted = True
                break
            except:
                continue

        if not deleted:
            raise FileNotFoundError(f"File not found: {pointer.oid}")

    def exists(self, pointer: LFSPointer) -> bool:
        """
        Check if file exists in Cloudinary.

        Args:
            pointer: LFS pointer containing the OID

        Returns:
            True if file exists, False otherwise
        """
        public_id = f"{self.folder}/{pointer.oid}"

        # Common file extensions to try (Cloudinary auto-adds these)
        extensions_to_try = ['', '.txt', '.bin', '.dat', '.png', '.jpg', '.jpeg', '.gif', '.mp4', '.pdf', '.zip']

        for ext in extensions_to_try:
            try:
                test_public_id = public_id + ext
                cloudinary.api.resource(
                    test_public_id,
                    resource_type="raw"
                )
                return True
            except cloudinary.api.NotFound:
                continue

        return False

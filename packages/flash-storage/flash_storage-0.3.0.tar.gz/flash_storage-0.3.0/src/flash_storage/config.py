"""Configuration management for Cloudinary credentials."""

import os
import json
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv


class CloudinaryConfig:
    """Manages storage configuration and credentials."""

    CONFIG_DIR = Path.home() / ".flash-storage"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    ENV_FILE = CONFIG_DIR / ".env"
    GDRIVE_CREDENTIALS = CONFIG_DIR / "gdrive_credentials.json"
    GDRIVE_TOKEN = CONFIG_DIR / "gdrive_token.json"
    STORAGE_PREFS = CONFIG_DIR / "storage_prefs.json"

    def has_gdrive(self) -> bool:
        """Check if Google Drive is configured."""
        return self.GDRIVE_TOKEN.exists()

    def setup_gdrive(self, client_id: str, client_secret: str, folder_id: Optional[str] = None) -> None:
        """
        Setup Google Drive OAuth credentials.

        Args:
            client_id: Google OAuth Client ID
            client_secret: Google OAuth Client Secret
            folder_id: Optional Google Drive folder ID for storing files
        """
        credentials_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "folder_id": folder_id or "root",
            "scopes": ["https://www.googleapis.com/auth/drive.file"]
        }

        with open(self.GDRIVE_CREDENTIALS, 'w') as f:
            json.dump(credentials_data, f, indent=2)

        print(f"✓ Google Drive credentials saved to {self.GDRIVE_CREDENTIALS}")
        print("ℹ Next step: Run OAuth authorization flow")

    def get_gdrive_credentials(self) -> Optional[Dict]:
        """Get Google Drive credentials from file."""
        if self.GDRIVE_CREDENTIALS.exists():
            with open(self.GDRIVE_CREDENTIALS, 'r') as f:
                return json.load(f)
        return None

    def get_gdrive_token(self) -> Optional[Dict]:
        """Get Google Drive access token from file."""
        if self.GDRIVE_TOKEN.exists():
            with open(self.GDRIVE_TOKEN, 'r') as f:
                return json.load(f)
        return None

    def save_gdrive_token(self, token_data: Dict) -> None:
        """Save Google Drive access token to file."""
        with open(self.GDRIVE_TOKEN, 'w') as f:
            json.dump(token_data, f, indent=2)

    def has_gdrive_credentials(self) -> bool:
        """Check if Google Drive credentials (Client ID/Secret) are saved."""
        return self.GDRIVE_CREDENTIALS.exists()

    def is_gdrive_configured(self) -> bool:
        """Check if Google Drive is fully configured with valid token."""
        return self.GDRIVE_CREDENTIALS.exists() and self.GDRIVE_TOKEN.exists()

    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = self.CONFIG_DIR
        self.config_file = self.CONFIG_FILE
        self.env_file = self.ENV_FILE
        self._ensure_config_dir()
        load_dotenv(self.env_file)

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def setup(self, cloud_name: str, api_key: str, api_secret: str,
              folder: Optional[str] = "git-lfs") -> None:
        """
        Setup Cloudinary configuration.

        Args:
            cloud_name: Cloudinary cloud name
            api_key: Cloudinary API key
            api_secret: Cloudinary API secret
            folder: Cloudinary folder for LFS files (default: git-lfs)
        """
        config_data = {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "folder": folder
        }

        # Save config to JSON (without secret)
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        # Save credentials to .env file
        env_content = f"""CLOUDINARY_CLOUD_NAME={cloud_name}
CLOUDINARY_API_KEY={api_key}
CLOUDINARY_API_SECRET={api_secret}
CLOUDINARY_FOLDER={folder}
"""
        with open(self.env_file, 'w') as f:
            f.write(env_content)

        print(f"✓ Configuration saved to {self.config_dir}")

    def get_credentials(self) -> Dict[str, str]:
        """
        Get Cloudinary credentials from environment.

        Returns:
            Dictionary with cloud_name, api_key, api_secret, and folder

        Raises:
            ValueError: If credentials are not configured
        """
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        folder = os.getenv("CLOUDINARY_FOLDER", "git-lfs")

        if not all([cloud_name, api_key, api_secret]):
            raise ValueError(
                "Cloudinary credentials not configured. "
                "Run 'flash setup' first."
            )

        return {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "api_secret": api_secret,
            "folder": folder
        }

    def is_configured(self) -> bool:
        """Check if Cloudinary is configured."""
        try:
            self.get_credentials()
            return True
        except ValueError:
            return False

    def get_config(self) -> Optional[Dict]:
        """Get configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return None

    def get_storage_prefs(self) -> Dict:
        """
        Get storage preferences.

        Returns:
            Dictionary with storage preferences
        """
        if self.STORAGE_PREFS.exists():
            with open(self.STORAGE_PREFS, 'r') as f:
                return json.load(f)
        return {
            "primary_storage": "cloudinary"  # Default to Cloudinary
        }

    def set_storage_pref(self, key: str, value) -> None:
        """
        Set a storage preference.

        Args:
            key: Preference key (e.g., 'primary_storage')
            value: Preference value
        """
        prefs = self.get_storage_prefs()
        prefs[key] = value

        with open(self.STORAGE_PREFS, 'w') as f:
            json.dump(prefs, f, indent=2)

    def get_primary_storage(self) -> str:
        """
        Get the primary storage backend.

        Returns:
            'cloudinary' or 'gdrive'
        """
        prefs = self.get_storage_prefs()
        return prefs.get("primary_storage", "cloudinary")

    def set_primary_storage(self, storage: str) -> None:
        """
        Set the primary storage backend.

        Args:
            storage: 'cloudinary' or 'gdrive'

        Raises:
            ValueError: If storage is not 'cloudinary' or 'gdrive'
        """
        if storage not in ['cloudinary', 'gdrive']:
            raise ValueError("Storage must be 'cloudinary' or 'gdrive'")

        self.set_storage_pref('primary_storage', storage)
        print(f"✓ Primary storage set to: {storage}")
        print(f"  Files will be uploaded to {storage} first, with automatic fallback to the other if full.")

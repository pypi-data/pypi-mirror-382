"""
Flash Storage
~~~~~~~~~~~~~

Multi-cloud storage manager with automatic fallback for Git LFS.
Supports Cloudinary and Google Drive with intelligent primary/fallback switching.
"""

__version__ = "0.3.0"
__author__ = "Your Name"

from .config import CloudinaryConfig
from .cloudinary_storage import CloudinaryStorage
from .gdrive_storage import GoogleDriveStorage
from .storage_manager import StorageManager
from .lfs_pointer import LFSPointer
from . import flash

__all__ = [
    "CloudinaryConfig",
    "CloudinaryStorage",
    "GoogleDriveStorage",
    "StorageManager",
    "LFSPointer",
    "flash"
]

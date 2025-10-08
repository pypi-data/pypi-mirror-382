"""Git LFS pointer file handling."""

import hashlib
from pathlib import Path
from typing import Dict, Optional


class LFSPointer:
    """Handles Git LFS pointer file creation and parsing."""

    VERSION = "https://git-lfs.github.com/spec/v1"

    def __init__(self, oid: str, size: int, cloudinary_url: Optional[str] = None):
        """
        Initialize LFS pointer.

        Args:
            oid: SHA256 hash of the file
            size: Size of the file in bytes
            cloudinary_url: Cloudinary URL for the file
        """
        self.oid = oid
        self.size = size
        self.cloudinary_url = cloudinary_url

    @classmethod
    def from_file(cls, file_path: Path) -> 'LFSPointer':
        """
        Create LFS pointer from a file.

        Args:
            file_path: Path to the file

        Returns:
            LFSPointer instance
        """
        # Calculate SHA256
        sha256 = hashlib.sha256()
        file_size = 0

        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
                file_size += len(chunk)

        oid = sha256.hexdigest()
        return cls(oid=oid, size=file_size)

    @classmethod
    def parse(cls, content: str) -> 'LFSPointer':
        """
        Parse LFS pointer file content.

        Args:
            content: Content of the pointer file

        Returns:
            LFSPointer instance
        """
        lines = content.strip().split('\n')
        data = {}

        for line in lines:
            if ' ' in line:
                key, value = line.split(' ', 1)
                data[key] = value

        if 'oid' in data and ':' in data['oid']:
            _, oid = data['oid'].split(':', 1)
        else:
            oid = data.get('oid', '')

        size = int(data.get('size', 0))
        cloudinary_url = data.get('cloudinary_url')

        return cls(oid=oid, size=size, cloudinary_url=cloudinary_url)

    def to_string(self) -> str:
        """
        Convert pointer to string format.

        Returns:
            Pointer file content as string
        """
        lines = [
            f"version {self.VERSION}",
            f"oid sha256:{self.oid}",
            f"size {self.size}"
        ]

        if self.cloudinary_url:
            lines.append(f"cloudinary_url {self.cloudinary_url}")

        return '\n'.join(lines) + '\n'

    def write(self, file_path: Path) -> None:
        """
        Write pointer to file.

        Args:
            file_path: Path where to write the pointer file
        """
        with open(file_path, 'w') as f:
            f.write(self.to_string())

    def to_dict(self) -> Dict:
        """Convert pointer to dictionary."""
        return {
            "oid": self.oid,
            "size": self.size,
            "cloudinary_url": self.cloudinary_url
        }

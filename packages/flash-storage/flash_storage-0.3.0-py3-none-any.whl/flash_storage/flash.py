"""
Flash Storage - Simple multi-cloud storage API

Usage:
    from flash_storage import flash as fs

    fs.push("myfile.psd")
    fs.pull("myfile.psd")
    fs.upload("myfile.psd")
"""

from pathlib import Path
from typing import Optional, Dict
from .config import CloudinaryConfig
from .storage_manager import StorageManager
from .lfs_pointer import LFSPointer


# Global instances (lazy initialization)
_config = None
_storage = None


def _get_storage() -> StorageManager:
    """Get or create storage manager instance."""
    global _config, _storage
    if _storage is None:
        _config = CloudinaryConfig()
        _storage = StorageManager(_config)
    return _storage


def setup(cloud_name: str, api_key: str, api_secret: str, folder: str = "git-lfs") -> None:
    """
    Setup Cloudinary credentials.

    Args:
        cloud_name: Your Cloudinary cloud name
        api_key: Your Cloudinary API key
        api_secret: Your Cloudinary API secret
        folder: Cloudinary folder for LFS files (default: git-lfs)

    Example:
        import flash as fs
        fs.setup("my-cloud", "123456", "secret", "my-folder")
    """
    config = CloudinaryConfig()
    config.setup(cloud_name, api_key, api_secret, folder)

    # Reset global instances to pick up new config
    global _config, _storage
    _config = None
    _storage = None


def push(file_path: str, message: Optional[str] = None, commit: bool = True) -> Dict[str, str]:
    """
    Push a file to Cloudinary (upload + replace with pointer + commit).

    Args:
        file_path: Path to the file to push
        message: Commit message (optional)
        commit: Whether to commit to git (default: True)

    Returns:
        Dictionary with 'oid', 'size', 'url', 'file'

    Example:
        import flash as fs
        result = fs.push("myfile.psd")
        print(result['url'])
    """
    import subprocess
    import shutil
    import tempfile

    storage = _get_storage()
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Save original to temp
    temp_file = Path(tempfile.gettempdir()) / f"{file_path_obj.name}.original"
    shutil.copy2(file_path_obj, temp_file)

    try:
        # Create pointer
        pointer = LFSPointer.from_file(file_path_obj)

        # Upload with automatic fallback support
        storage_name, url_or_id = storage.upload_with_fallback(file_path_obj, pointer)

        # Replace with pointer
        pointer.write(file_path_obj)

        # Commit if requested
        if commit:
            try:
                subprocess.run(['git', 'add', str(file_path_obj)],
                             check=True, capture_output=True)
                commit_msg = message or f"Add {file_path_obj.name}"
                subprocess.run(['git', 'commit', '-m', commit_msg],
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                pass  # Git operations are optional

        # Clean up temp file
        temp_file.unlink()

        return {
            'oid': pointer.oid,
            'size': pointer.size,
            'url': url_or_id,
            'storage': storage_name,
            'file': str(file_path_obj)
        }

    except Exception as e:
        # Restore original file
        if temp_file.exists():
            shutil.copy2(temp_file, file_path_obj)
            temp_file.unlink()
        raise RuntimeError(f"Push failed: {e}")


def pull(file_path: str) -> Dict[str, str]:
    """
    Pull a file from Cloudinary (replace pointer with actual file).

    Args:
        file_path: Path to the LFS pointer file

    Returns:
        Dictionary with 'oid', 'size', 'file'

    Example:
        import flash as fs
        result = fs.pull("myfile.psd")
        print(f"Downloaded {result['size']} bytes")
    """
    import shutil
    import tempfile

    storage = _get_storage()
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read pointer
    with open(file_path_obj, 'r') as f:
        content = f.read()

    if not content.startswith('version https://git-lfs.github.com/spec'):
        raise ValueError(f"{file_path} is not an LFS pointer file")

    # Parse pointer
    pointer = LFSPointer.parse(content)

    # Download to temp
    temp_file = Path(tempfile.gettempdir()) / f"{file_path_obj.name}.download"
    storage.download(pointer, temp_file)

    # Replace pointer with actual file
    shutil.move(str(temp_file), str(file_path_obj))

    return {
        'oid': pointer.oid,
        'size': pointer.size,
        'file': str(file_path_obj)
    }


def upload(file_path: str) -> Dict[str, str]:
    """
    Upload a file to storage (without replacing local file).

    Args:
        file_path: Path to the file to upload

    Returns:
        Dictionary with 'oid', 'size', 'url', 'storage', 'file'

    Example:
        import flash as fs
        result = fs.upload("myfile.psd")
        print(result['url'])
    """
    storage = _get_storage()
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Create pointer
    pointer = LFSPointer.from_file(file_path_obj)

    # Upload with automatic fallback support
    storage_name, url_or_id = storage.upload_with_fallback(file_path_obj, pointer)

    return {
        'oid': pointer.oid,
        'size': pointer.size,
        'url': url_or_id,
        'storage': storage_name,
        'file': str(file_path_obj)
    }


def download(oid: str, output_path: str, size: int = 0) -> Dict[str, str]:
    """
    Download a file from Cloudinary by OID.

    Args:
        oid: SHA256 hash of the file
        output_path: Where to save the file
        size: File size in bytes (optional)

    Returns:
        Dictionary with 'oid', 'file'

    Example:
        import flash as fs
        fs.download("abc123...", "myfile.psd")
    """
    storage = _get_storage()
    output_path_obj = Path(output_path)

    # Create pointer
    pointer = LFSPointer(oid=oid, size=size)

    # Download
    storage.download(pointer, output_path_obj)

    return {
        'oid': oid,
        'file': str(output_path_obj)
    }


def exists(file_path: str) -> bool:
    """
    Check if a file exists in any configured storage.

    Args:
        file_path: Path to the file or LFS pointer

    Returns:
        True if file exists in any storage, False otherwise

    Example:
        import flash as fs
        if fs.exists("myfile.psd"):
            print("File is in storage!")
    """
    storage = _get_storage()
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        return False

    # Try to create pointer from file
    try:
        pointer = LFSPointer.from_file(file_path_obj)
    except Exception:
        # Maybe it's a pointer file?
        try:
            with open(file_path_obj, 'r') as f:
                content = f.read()
            pointer = LFSPointer.parse(content)
        except Exception:
            return False

    exists_result, _ = storage.exists(pointer)
    return exists_result


def delete(file_path: str) -> Dict[str, str]:
    """
    Delete a file from Cloudinary.

    Args:
        file_path: Path to the file or LFS pointer

    Returns:
        Dictionary with 'oid', 'status'

    Example:
        import flash as fs
        fs.delete("myfile.psd")
    """
    storage = _get_storage()
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Create pointer
    pointer = LFSPointer.from_file(file_path_obj)

    # Delete
    storage.delete(pointer)

    return {
        'oid': pointer.oid,
        'status': 'deleted'
    }


def info(file_path: str) -> Dict[str, any]:
    """
    Get information about a file.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file information

    Example:
        import flash as fs
        info = fs.info("myfile.psd")
        print(info)
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check if it's a pointer
    try:
        with open(file_path_obj, 'r') as f:
            content = f.read()

        if content.startswith('version https://git-lfs.github.com/spec'):
            pointer = LFSPointer.parse(content)
            storage = _get_storage()
            exists_result, storage_name = storage.exists(pointer)

            return {
                'file': str(file_path_obj),
                'type': 'lfs_pointer',
                'oid': pointer.oid,
                'size': pointer.size,
                'exists_in_storage': exists_result,
                'storage_location': storage_name
            }
    except Exception:
        pass

    # Regular file
    pointer = LFSPointer.from_file(file_path_obj)
    storage = _get_storage()
    exists_result, storage_name = storage.exists(pointer)

    return {
        'file': str(file_path_obj),
        'type': 'regular_file',
        'oid': pointer.oid,
        'size': pointer.size,
        'exists_in_storage': exists_result,
        'storage_location': storage_name
    }


def status() -> Dict[str, any]:
    """
    Get storage configuration status.

    Returns:
        Dictionary with configuration status

    Example:
        import flash as fs
        status = fs.status()
        print(status['cloudinary']['configured'])
    """
    config = CloudinaryConfig()

    result = {
        'config_dir': str(config.config_dir),
        'cloudinary': {
            'configured': config.is_configured()
        },
        'google_drive': {
            'configured': config.is_gdrive_configured()
        },
        'primary_storage': config.get_primary_storage()
    }

    if config.is_configured():
        creds = config.get_credentials()
        result['cloudinary'].update({
            'cloud_name': creds['cloud_name'],
            'api_key': creds['api_key'][:4] + '***',
            'folder': creds['folder']
        })

    if config.is_gdrive_configured():
        gdrive_creds = config.get_gdrive_credentials()
        if gdrive_creds:
            result['google_drive'].update({
                'folder_id': gdrive_creds.get('folder_id', 'root')
            })

    return result


# Convenience aliases
up = upload
down = download
rm = delete
ls = info

"""Command-line interface for Flash Storage."""

import sys
import subprocess
from pathlib import Path
import click
from .config import CloudinaryConfig
from .storage_manager import StorageManager
from .lfs_pointer import LFSPointer
from .transfer_agent import TransferAgent


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Git LFS integration with Cloudinary for binary media storage."""
    pass


@cli.command()
@click.option('--cloud-name', prompt='Cloudinary Cloud Name',
              help='Your Cloudinary cloud name')
@click.option('--api-key', prompt='Cloudinary API Key',
              help='Your Cloudinary API key')
@click.option('--api-secret', prompt='Cloudinary API Secret',
              hide_input=True, help='Your Cloudinary API secret')
@click.option('--folder', default='git-lfs',
              help='Cloudinary folder for LFS files (default: git-lfs)')
def setup(cloud_name: str, api_key: str, api_secret: str, folder: str):
    """
    Setup Cloudinary credentials.

    This command will prompt you for your Cloudinary account details
    and save them securely for future use.
    """
    config = CloudinaryConfig()
    config.setup(cloud_name, api_key, api_secret, folder)

    click.echo("\n" + "="*60)
    click.echo("[SUCCESS] Cloudinary configuration saved successfully!")
    click.echo("="*60)
    click.echo("\nNext steps:")
    click.echo("1. Run 'flash init' in your Git repository")
    click.echo("2. Add files to track with Git LFS")
    click.echo("   Example: git lfs track '*.psd'")
    click.echo("3. Commit and push as usual!")
    click.echo("\nYour binary files will now be stored in Cloudinary.")


@cli.command(name='setup-gdrive')
@click.option('--client-id', prompt='Google OAuth Client ID',
              help='Your Google OAuth Client ID')
@click.option('--client-secret', prompt='Google OAuth Client Secret',
              hide_input=True, help='Your Google OAuth Client Secret')
@click.option('--folder-id', default=None,
              help='Google Drive folder ID (optional, will create default folder)')
def setup_gdrive(client_id: str, client_secret: str, folder_id: str):
    """
    Setup Google Drive OAuth credentials.

    This command will prompt you for your Google OAuth credentials and
    save them for fallback storage when Cloudinary is full.

    To get your credentials:
    1. Go to https://console.cloud.google.com/
    2. Create/select a project
    3. Enable Google Drive API
    4. Create OAuth 2.0 Client ID credentials (type: Desktop app)
    5. Copy the Client ID and Client Secret
    """
    config = CloudinaryConfig()
    config.setup_gdrive(client_id, client_secret, folder_id)

    click.echo("\n" + "="*60)
    click.echo("[SUCCESS] Google Drive credentials saved!")
    click.echo("="*60)
    click.echo("\nGoogle Drive is now configured as fallback storage.")
    click.echo("When Cloudinary storage is full, files will automatically")
    click.echo("be uploaded to Google Drive.")
    click.echo("\nTo set Google Drive as your primary storage:")
    click.echo("  flash set-primary gdrive")
    click.echo("\nTest the authorization by uploading a file:")
    click.echo("  flash push <file>")


@cli.command(name='set-primary')
@click.argument('storage', type=click.Choice(['cloudinary', 'gdrive'], case_sensitive=False))
def set_primary(storage: str):
    """
    Set the primary storage backend.

    Files will be uploaded to the primary storage first, with automatic
    fallback to the secondary storage if the primary is full.

    STORAGE: Either 'cloudinary' or 'gdrive'

    Examples:
        flash set-primary cloudinary
        flash set-primary gdrive
    """
    config = CloudinaryConfig()

    storage = storage.lower()

    # Check if the selected storage is configured
    if storage == 'cloudinary' and not config.is_configured():
        click.echo("[ERROR] Cloudinary is not configured.")
        click.echo("Run 'flash setup' first.")
        sys.exit(1)

    if storage == 'gdrive' and not config.has_gdrive_credentials():
        click.echo("[ERROR] Google Drive is not configured.")
        click.echo("Run 'flash setup-gdrive' first.")
        sys.exit(1)

    config.set_primary_storage(storage)

    storage_display = "Cloudinary" if storage == "cloudinary" else "Google Drive"
    fallback_display = "Google Drive" if storage == "cloudinary" else "Cloudinary"

    click.echo("\n" + "="*60)
    click.echo("[SUCCESS] Primary storage updated!")
    click.echo("="*60)
    click.echo(f"\n✓ Primary: {storage_display}")
    click.echo(f"  Fallback: {fallback_display}")
    click.echo(f"\nAll uploads will now use {storage_display} first.")
    click.echo(f"If {storage_display} is full, files will automatically")
    click.echo(f"be uploaded to {fallback_display}.")


@cli.command()
def init():
    """
    Initialize Git LFS with Cloudinary in the current repository.

    This configures Git LFS to use Cloudinary as a custom transfer agent.
    """
    config = CloudinaryConfig()

    if not config.is_configured():
        click.echo("❌ Cloudinary not configured. Run 'flash setup' first.")
        sys.exit(1)

    # Check if we're in a git repository
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'],
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        click.echo("[ERROR] Not in a Git repository. Please run this command in a Git repository.")
        sys.exit(1)

    # Initialize Git LFS if not already
    try:
        subprocess.run(['git', 'lfs', 'install'], check=True, capture_output=True)
        click.echo("[OK] Git LFS initialized")
    except subprocess.CalledProcessError:
        click.echo("[ERROR] Failed to initialize Git LFS. Is it installed?")
        sys.exit(1)

    # Configure custom transfer agent
    commands = [
        ['git', 'config', 'lfs.customtransfer.cloudinary.path', 'flash-agent'],
        ['git', 'config', 'lfs.standalonetransferagent', 'cloudinary'],
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"[ERROR] Failed to configure Git LFS: {e}")
            sys.exit(1)

    click.echo("\n" + "="*60)
    click.echo("[SUCCESS] Git LFS configured to use Cloudinary!")
    click.echo("="*60)
    click.echo("\nYou can now track files with Git LFS:")
    click.echo("  git lfs track '*.psd'")
    click.echo("  git lfs track '*.mp4'")
    click.echo("  git lfs track '*.zip'")
    click.echo("\nBinary files will be automatically uploaded to Cloudinary.")


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--message', '-m', help='Commit message (default: "Add <filename>")')
@click.option('--no-commit', is_flag=True, help='Skip git commit')
def push(file_path: str, message: str, no_commit: bool):
    """
    Push a file to Cloudinary, replace with pointer, and commit to git.

    This is the simple one-command workflow:
    1. Uploads the binary file to Cloudinary
    2. Replaces the local file with an LFS pointer
    3. Commits the pointer to git (unless --no-commit)

    FILE_PATH: Path to the file to push
    """
    config = CloudinaryConfig()

    if not config.is_configured():
        click.echo("[ERROR] Cloudinary not configured. Run 'flash setup' first.")
        sys.exit(1)

    try:
        storage = StorageManager(config)
        file_path_obj = Path(file_path)

        # Save original file to temp location
        import tempfile
        import shutil
        temp_file = Path(tempfile.gettempdir()) / f"{file_path_obj.name}.original"
        shutil.copy2(file_path_obj, temp_file)

        click.echo(f"Processing {file_path_obj.name}...")

        # Create pointer from original file
        pointer = LFSPointer.from_file(file_path_obj)

        # Upload with automatic fallback support
        click.echo(f"Uploading to storage...")
        storage_name, url_or_id = storage.upload_with_fallback(file_path_obj, pointer)

        storage_display = "Cloudinary" if storage_name == "cloudinary" else "Google Drive"
        click.echo(f"[OK] Uploaded to {storage_display}")

        # Replace file with pointer
        pointer.write(file_path_obj)
        click.echo(f"[OK] Replaced file with LFS pointer")

        # Stage and commit
        if not no_commit:
            try:
                # Stage the file
                subprocess.run(['git', 'add', str(file_path_obj)],
                             check=True, capture_output=True)
                click.echo(f"[OK] Staged for commit")

                # Commit
                commit_msg = message or f"Add {file_path_obj.name}"
                subprocess.run(['git', 'commit', '-m', commit_msg],
                             check=True, capture_output=True)
                click.echo(f"[OK] Committed to git")

            except subprocess.CalledProcessError as e:
                click.echo(f"[WARNING] Could not commit. Run 'git commit -m \"Add {file_path_obj.name}\"' manually")

        # Clean up temp file
        temp_file.unlink()

        click.echo(f"\n[SUCCESS] File pushed successfully!")
        click.echo(f"  File: {file_path_obj}")
        click.echo(f"  Storage: {storage_display}")
        click.echo(f"  OID: {pointer.oid}")
        click.echo(f"  Size: {pointer.size} bytes")
        if storage_name == "cloudinary":
            click.echo(f"  URL: {url_or_id}")
        else:
            click.echo(f"  File ID: {url_or_id}")
        if not no_commit:
            click.echo(f"\nNext step: git push")
        else:
            click.echo(f"\nNext step: git commit -m \"Add {file_path_obj.name}\" && git push")

    except Exception as e:
        click.echo(f"[ERROR] Push failed: {e}")
        # Restore original file if exists
        if temp_file.exists():
            shutil.copy2(temp_file, file_path_obj)
            temp_file.unlink()
            click.echo("[OK] Restored original file")
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def upload(file_path: str):
    """
    Upload a file to Cloudinary (without replacing local file).

    FILE_PATH: Path to the file to upload
    """
    config = CloudinaryConfig()

    if not config.is_configured():
        click.echo("[ERROR] Cloudinary not configured. Run 'flash setup' first.")
        sys.exit(1)

    try:
        storage = StorageManager(config)
        file_path_obj = Path(file_path)

        click.echo(f"Uploading {file_path_obj.name}...")

        # Create pointer
        pointer = LFSPointer.from_file(file_path_obj)

        # Upload with automatic fallback support
        storage_name, url_or_id = storage.upload_with_fallback(file_path_obj, pointer)

        storage_display = "Cloudinary" if storage_name == "cloudinary" else "Google Drive"

        click.echo(f"\n[SUCCESS] File uploaded successfully!")
        click.echo(f"  Storage: {storage_display}")
        click.echo(f"  OID: {pointer.oid}")
        click.echo(f"  Size: {pointer.size} bytes")
        if storage_name == "cloudinary":
            click.echo(f"  URL: {url_or_id}")
        else:
            click.echo(f"  File ID: {url_or_id}")

    except Exception as e:
        click.echo(f"[ERROR] Upload failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def pull(file_path: str):
    """
    Pull a file from Cloudinary and replace the LFS pointer with the actual file.

    This reads an LFS pointer file, downloads the binary from Cloudinary,
    and replaces the pointer with the actual file.

    FILE_PATH: Path to the LFS pointer file
    """
    config = CloudinaryConfig()

    if not config.is_configured():
        click.echo("[ERROR] Cloudinary not configured. Run 'flash setup' first.")
        sys.exit(1)

    try:
        storage = StorageManager(config)
        file_path_obj = Path(file_path)

        # Read pointer file
        with open(file_path_obj, 'r') as f:
            content = f.read()

        # Check if it's a pointer file
        if not content.startswith('version https://git-lfs.github.com/spec'):
            click.echo(f"[ERROR] {file_path_obj.name} is not an LFS pointer file")
            sys.exit(1)

        # Parse pointer
        pointer = LFSPointer.parse(content)

        click.echo(f"Pulling {file_path_obj.name} from storage...")
        click.echo(f"  OID: {pointer.oid}")

        # Download to temp file first
        import tempfile
        temp_file = Path(tempfile.gettempdir()) / f"{file_path_obj.name}.download"
        storage.download(pointer, temp_file)

        # Replace pointer with actual file
        import shutil
        shutil.move(str(temp_file), str(file_path_obj))

        click.echo(f"\n[SUCCESS] File pulled successfully!")
        click.echo(f"  File: {file_path_obj}")
        click.echo(f"  Size: {pointer.size} bytes")

    except Exception as e:
        click.echo(f"[ERROR] Pull failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument('oid')
@click.argument('output_path', type=click.Path())
@click.option('--size', type=int, help='File size in bytes')
def download(oid: str, output_path: str, size: int):
    """
    Download a file from Cloudinary by OID.

    OID: SHA256 hash of the file
    OUTPUT_PATH: Where to save the downloaded file
    """
    config = CloudinaryConfig()

    if not config.is_configured():
        click.echo("[ERROR] Cloudinary not configured. Run 'flash setup' first.")
        sys.exit(1)

    try:
        storage = StorageManager(config)
        output_path_obj = Path(output_path)

        click.echo(f"Downloading {oid[:8]}...")

        # Create pointer
        pointer = LFSPointer(oid=oid, size=size or 0)

        # Download
        storage.download(pointer, output_path_obj)

        click.echo(f"[OK] File downloaded to {output_path}")

    except Exception as e:
        click.echo(f"[ERROR] Download failed: {e}")
        sys.exit(1)


@cli.command()
def verify():
    """Verify Cloudinary credentials by testing the connection."""
    config = CloudinaryConfig()

    if not config.is_configured():
        click.echo("[ERROR] Cloudinary not configured. Run setup first.")
        sys.exit(1)

    click.echo("Verifying Cloudinary credentials...")

    try:
        import cloudinary
        import cloudinary.api

        # Get credentials
        creds = config.get_credentials()

        # Configure Cloudinary
        cloudinary.config(
            cloud_name=creds["cloud_name"],
            api_key=creds["api_key"],
            api_secret=creds["api_secret"],
            secure=True
        )

        # Test the connection by calling the API
        result = cloudinary.api.ping()

        click.echo("\n" + "="*60)
        click.echo("[SUCCESS] Cloudinary credentials are valid!")
        click.echo("="*60)
        click.echo(f"\n  Cloud Name: {creds['cloud_name']}")
        click.echo(f"  API Key: {creds['api_key'][:4]}{'*' * (len(creds['api_key']) - 4)}")
        click.echo(f"  API Secret: {creds['api_secret'][:4]}{'*' * (len(creds['api_secret']) - 4)}")
        click.echo(f"  Folder: {creds['folder']}")
        click.echo(f"\n  Status: {result.get('status', 'ok')}")

    except Exception as e:
        click.echo("\n" + "="*60)
        click.echo("[ERROR] Cloudinary credentials are INVALID")
        click.echo("="*60)
        click.echo(f"\nError: {e}")
        click.echo("\nPlease run 'flash setup' to reconfigure.")
        sys.exit(1)


@cli.command()
def config():
    """Show current Cloudinary configuration."""
    cfg = CloudinaryConfig()

    click.echo("\n" + "="*60)
    click.echo("Cloudinary Configuration")
    click.echo("="*60)

    if cfg.is_configured():
        creds = cfg.get_credentials()
        click.echo(f"\n  Cloud Name: {creds['cloud_name']}")
        click.echo(f"  API Key: {creds['api_key']}")
        click.echo(f"  API Secret: {creds['api_secret'][:4]}{'*' * (len(creds['api_secret']) - 4)}")
        click.echo(f"  Folder: {creds['folder']}")
        click.echo(f"  Config Dir: {cfg.config_dir}")
        click.echo(f"\nRun 'flash verify' to test credentials.")
    else:
        click.echo("\n[NOT CONFIGURED] Cloudinary not configured")
        click.echo("Run 'flash setup' to configure")


@cli.command()
def status():
    """Check storage configuration status."""
    config = CloudinaryConfig()

    click.echo("\n" + "="*60)
    click.echo("Git LFS Storage Status")
    click.echo("="*60)

    # Cloudinary status
    if config.is_configured():
        creds = config.get_credentials()
        click.echo(f"\n[OK] Cloudinary configured")
        click.echo(f"  Cloud Name: {creds['cloud_name']}")
        click.echo(f"  API Key: {creds['api_key'][:4]}{'*' * (len(creds['api_key']) - 4)}")
        click.echo(f"  Folder: {creds['folder']}")

        # Quick credential verification
        click.echo(f"\n  Run 'flash verify' to test credentials")
    else:
        click.echo("\n[NOT CONFIGURED] Cloudinary not configured")
        click.echo("  Run 'flash setup' to configure")

    # Google Drive status
    if config.is_gdrive_configured():
        click.echo(f"\n[OK] Google Drive configured")
        gdrive_creds = config.get_gdrive_credentials()
        if gdrive_creds:
            click.echo(f"  Folder ID: {gdrive_creds.get('folder_id', 'root')}")
        click.echo(f"  Token: {'Valid' if config.get_gdrive_token() else 'Not authorized yet'}")
    else:
        click.echo("\n[NOT CONFIGURED] Google Drive not configured")
        click.echo("  Run 'flash setup-gdrive' to configure")

    # Storage preferences
    primary = config.get_primary_storage()
    primary_display = "Cloudinary" if primary == "cloudinary" else "Google Drive"
    fallback_display = "Google Drive" if primary == "cloudinary" else "Cloudinary"

    click.echo(f"\n[STORAGE PRIORITY]")
    click.echo(f"  Primary: {primary_display}")
    click.echo(f"  Fallback: {fallback_display} (automatic)")
    click.echo(f"\n  Change with: flash set-primary <cloudinary|gdrive>")

    click.echo(f"\n[CONFIG DIR] {config.config_dir}")

    # Check Git LFS
    try:
        result = subprocess.run(['git', 'lfs', 'version'],
                              capture_output=True, text=True, check=True)
        click.echo(f"\n[OK] Git LFS installed")
        click.echo(f"  {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("\n[NOT INSTALLED] Git LFS not installed")
        click.echo("  Install from: https://git-lfs.github.com/")


@cli.command(name='agent')
def run_agent():
    """
    Run the transfer agent (internal use by Git LFS).

    This command is called by Git LFS and should not be run manually.
    """
    agent = TransferAgent()
    agent.run()


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()

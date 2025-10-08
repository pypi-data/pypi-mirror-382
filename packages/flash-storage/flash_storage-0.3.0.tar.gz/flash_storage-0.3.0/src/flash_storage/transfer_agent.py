"""Git LFS custom transfer agent for Cloudinary."""

import sys
import json
from pathlib import Path
from typing import Dict, Any
from .config import CloudinaryConfig
from .cloudinary_storage import CloudinaryStorage
from .lfs_pointer import LFSPointer


class TransferAgent:
    """Git LFS custom transfer agent implementation."""

    def __init__(self):
        """Initialize transfer agent."""
        self.config = CloudinaryConfig()
        self.storage = CloudinaryStorage(self.config)

    def send_response(self, response: Dict[str, Any]) -> None:
        """
        Send response to Git LFS.

        Args:
            response: Response dictionary to send
        """
        json_response = json.dumps(response)
        sys.stdout.write(json_response + '\n')
        sys.stdout.flush()

    def read_request(self) -> Dict[str, Any]:
        """
        Read request from Git LFS.

        Returns:
            Request dictionary
        """
        line = sys.stdin.readline()
        if not line:
            return {}
        return json.loads(line)

    def handle_init(self) -> None:
        """Handle initialization request."""
        # Send empty response to acknowledge
        self.send_response({})

    def handle_upload(self, request: Dict[str, Any]) -> None:
        """
        Handle upload request.

        Args:
            request: Upload request from Git LFS
        """
        oid = request.get('oid')
        size = request.get('size')
        path = request.get('path')

        try:
            # Create pointer
            pointer = LFSPointer(oid=oid, size=size)

            # Upload to Cloudinary
            file_path = Path(path)
            cloudinary_url = self.storage.upload(file_path, pointer)

            # Send success response
            self.send_response({
                'event': 'complete',
                'oid': oid
            })

        except Exception as e:
            # Send error response
            self.send_response({
                'event': 'error',
                'oid': oid,
                'error': {
                    'code': 1,
                    'message': str(e)
                }
            })

    def handle_download(self, request: Dict[str, Any]) -> None:
        """
        Handle download request.

        Args:
            request: Download request from Git LFS
        """
        oid = request.get('oid')
        size = request.get('size')
        path = request.get('path')

        try:
            # Create pointer
            pointer = LFSPointer(oid=oid, size=size)

            # Download from Cloudinary
            output_path = Path(path)
            self.storage.download(pointer, output_path)

            # Send success response
            self.send_response({
                'event': 'complete',
                'oid': oid
            })

        except Exception as e:
            # Send error response
            self.send_response({
                'event': 'error',
                'oid': oid,
                'error': {
                    'code': 2,
                    'message': str(e)
                }
            })

    def handle_terminate(self) -> None:
        """Handle termination request."""
        # Send empty response and exit
        self.send_response({})
        sys.exit(0)

    def run(self) -> None:
        """Run the transfer agent."""
        while True:
            request = self.read_request()

            if not request:
                continue

            event = request.get('event')

            if event == 'init':
                self.handle_init()
            elif event == 'upload':
                self.handle_upload(request)
            elif event == 'download':
                self.handle_download(request)
            elif event == 'terminate':
                self.handle_terminate()
            else:
                # Unknown event, send error
                self.send_response({
                    'error': {
                        'code': 3,
                        'message': f'Unknown event: {event}'
                    }
                })


def main():
    """Main entry point for transfer agent."""
    agent = TransferAgent()
    agent.run()


if __name__ == '__main__':
    main()

"""
AI Code Tools Server - Background server for tool execution.

Simple HTTP server that runs in Docker container and handles tool execution requests.
Provides REST API for read, write, edit, and run operations.
"""

import json
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any
import logging

from aicodetools.tools import ReadTool, WriteTool, EditTool, RunTool


class CodeToolsHandler(BaseHTTPRequestHandler):
    """HTTP request handler for code tools API."""

    # Shared tool instances across all handler instances
    _shared_read_tool = None
    _shared_write_tool = None
    _shared_edit_tool = None
    _shared_run_tool = None

    def __init__(self, *args, **kwargs):
        # Initialize shared tools if not already done
        if CodeToolsHandler._shared_read_tool is None:
            CodeToolsHandler._shared_read_tool = ReadTool()
            CodeToolsHandler._shared_write_tool = WriteTool()
            CodeToolsHandler._shared_edit_tool = EditTool()
            CodeToolsHandler._shared_run_tool = RunTool()

        # Reference shared instances
        self.read_tool = CodeToolsHandler._shared_read_tool
        self.write_tool = CodeToolsHandler._shared_write_tool
        self.edit_tool = CodeToolsHandler._shared_edit_tool
        self.run_tool = CodeToolsHandler._shared_run_tool
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle POST requests for tool operations."""
        try:
            # Parse request path
            path = urlparse(self.path).path

            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                request_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            else:
                request_data = {}

            # Route to appropriate tool
            if path == '/api/read':
                response = self._handle_read(request_data)
            elif path == '/api/write':
                response = self._handle_write(request_data)
            elif path == '/api/edit':
                response = self._handle_edit(request_data)
            elif path == '/api/run':
                response = self._handle_run(request_data)
            elif path == '/api/get_output':
                response = self._handle_get_output(request_data)
            elif path == '/api/send_input':
                response = self._handle_send_input(request_data)
            elif path == '/api/stop_process':
                response = self._handle_stop_process(request_data)
            elif path == '/api/get_status':
                response = self._handle_get_status()
            else:
                response = {"success": False, "error": f"Unknown endpoint: {path}"}

            self._send_json_response(response)

        except Exception as e:
            error_response = {"success": False, "error": f"Server error: {str(e)}"}
            self._send_json_response(error_response, status_code=500)

    def do_GET(self):
        """Handle GET requests for status and information."""
        try:
            path = urlparse(self.path).path

            if path == '/api/status':
                response = {
                    "success": True,
                    "status": "running",
                    "version": "1.0.0",
                    "tools": ["read", "write", "edit", "run"],
                    "message": "AI Code Tools server is running"
                }
            elif path == '/api/get_status':
                response = self._handle_get_status()
            else:
                response = {"success": False, "error": f"Unknown GET endpoint: {path}"}

            self._send_json_response(response)

        except Exception as e:
            error_response = {"success": False, "error": f"Server error: {str(e)}"}
            self._send_json_response(error_response, status_code=500)

    def _handle_read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle read tool requests with flattened parameters."""
        file_path = data.get('file_path')
        if not file_path:
            return {"success": False, "error": "file_path is required"}

        # Link read and write tools for safety
        self.write_tool.mark_file_as_read(file_path)
        self.edit_tool.mark_file_as_read(file_path)

        # Extract flattened parameters
        lines_start = data.get('lines_start')
        lines_end = data.get('lines_end')
        regex = data.get('regex')

        return self.read_tool.read_file(
            file_path=file_path,
            lines_start=lines_start,
            lines_end=lines_end,
            regex=regex
        )

    def _handle_write(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle write tool requests with simplified API."""
        file_path = data.get('file_path')
        content = data.get('content')

        if not file_path:
            return {"success": False, "error": "file_path is required"}
        if content is None:
            return {"success": False, "error": "content is required"}

        return self.write_tool.write_file(file_path, content)

    def _handle_edit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle edit tool requests with simplified API."""
        file_path = data.get('file_path')
        old_string = data.get('old_string')
        new_string = data.get('new_string')

        if not file_path:
            return {"success": False, "error": "file_path is required"}
        if old_string is None:
            return {"success": False, "error": "old_string is required"}
        if new_string is None:
            return {"success": False, "error": "new_string is required"}

        return self.edit_tool.edit_file(
            file_path, old_string, new_string, data.get('replace_all', False)
        )

    def _handle_run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle run tool requests with simplified API."""
        command = data.get('command')
        if command is None:
            return {"success": False, "error": "command is required"}

        return self.run_tool.run_command(
            command=command,
            timeout=data.get('timeout', 300),
            interactive=data.get('interactive', False)
        )

    def _handle_get_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get output requests for active process."""
        return self.run_tool.get_output(
            max_lines=data.get('max_lines', 100)
        )

    def _handle_send_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send input requests to active process."""
        input_text = data.get('input_text')
        if input_text is None:
            return {"success": False, "error": "input_text is required"}

        return self.run_tool.send_input(input_text)

    def _handle_stop_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stop active process requests."""
        return self.run_tool.stop_process(
            force=data.get('force', False)
        )

    def _handle_get_status(self) -> Dict[str, Any]:
        """Handle get status requests for active process."""
        return self.run_tool.get_status()

    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Override to use proper logging."""
        logging.info(f"{self.address_string()} - {format % args}")


class CodeToolsServer:
    """AI Code Tools HTTP Server."""

    def __init__(self, host: str = '0.0.0.0', port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None

    def start(self):
        """Start the server."""
        try:
            # Set up logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

            self.server = HTTPServer((self.host, self.port), CodeToolsHandler)

            logging.info(f"Starting AI Code Tools server on {self.host}:{self.port}")
            logging.info("Available endpoints:")
            logging.info("  POST /api/read - Read file content")
            logging.info("  POST /api/write - Write file content")
            logging.info("  POST /api/edit - Edit file content")
            logging.info("  POST /api/run - Run command (interactive flag controls mode)")
            logging.info("  POST /api/get_output - Get output from active process")
            logging.info("  POST /api/send_input - Send input to active process")
            logging.info("  POST /api/stop_process - Stop active process")
            logging.info("  GET /api/status - Server status")
            logging.info("  GET /api/get_status - Get active process status")

            self.server.serve_forever()

        except KeyboardInterrupt:
            logging.info("Server stopped by user")
        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            if self.server:
                self.server.shutdown()
                self.server.server_close()

    def start_background(self):
        """Start server in background thread."""
        if self.server_thread and self.server_thread.is_alive():
            return False  # Already running

        self.server_thread = threading.Thread(target=self.start, daemon=True)
        self.server_thread.start()
        time.sleep(1)  # Give server time to start
        return True

    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)


def main():
    """Main server entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='AI Code Tools Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--port', type=int, default=8080, help='Server port (container internal)')

    args = parser.parse_args()

    server = CodeToolsServer(host=args.host, port=args.port)
    server.start()


if __name__ == '__main__':
    main()
"""
AI Code Tools Client Manager - Manages multiple Docker instances and clients.

Provides orchestration for multiple CodeToolsClient instances, each running in
isolated Docker containers with unique ports, container names, and log directories.
Supports threading and concurrent operations across multiple agents.
"""

import os
import socket
import threading
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .client import CodeToolsClient


class ClientManager:
    """Manager for multiple CodeToolsClient instances with isolated Docker containers."""

    def __init__(self, docker_image: str = "python:3.11-slim", base_log_dir: str = "./logs"):
        """
        Initialize ClientManager.

        Args:
            docker_image: Docker image to use for all client containers
            base_log_dir: Base directory for logs, client logs go in {base_log_dir}/{id}/
        """
        self.docker_image = docker_image
        self.base_log_dir = base_log_dir

        # Thread-safe client registry
        self._clients: Dict[str, Dict[str, Any]] = {}
        self._used_ports: set = set()
        self._lock = threading.RLock()

        # Starting port for allocation
        self._start_port = 18080

        # Ensure base log directory exists
        if base_log_dir:
            os.makedirs(base_log_dir, exist_ok=True)

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available for use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return False

    def _find_available_port(self) -> int:
        """Find the next available port starting from _start_port."""
        port = self._start_port
        max_attempts = 1000  # Try up to 1000 ports
        attempts = 0

        while port < 65535 and attempts < max_attempts:
            if port not in self._used_ports and self._is_port_available(port):
                # Double-check port is still available (prevent race conditions)
                if self._is_port_available(port):
                    self._used_ports.add(port)
                    return port
            port += 1
            attempts += 1

        raise RuntimeError("No available ports found after checking 1000 ports")

    def get_client(self, id: str) -> CodeToolsClient:
        """
        Get or create a CodeToolsClient for the given ID.

        Args:
            id: Unique identifier for the client

        Returns:
            CodeToolsClient instance configured for this ID
        """
        with self._lock:
            # Return existing client if already created
            if id in self._clients:
                client_info = self._clients[id]
                if client_info['client'] and hasattr(client_info['client'], 'docker_container'):
                    return client_info['client']

            # Try to create client with automatic port retry
            max_port_retries = 5
            for attempt in range(max_port_retries):
                try:
                    # Create new client
                    unique_id = str(uuid.uuid4())[:8]  # Short UUID for container name
                    port = self._find_available_port()
                    container_name = f"aicodetools-{id}-{unique_id}"

                    # Set up log directory
                    log_folder = None
                    if self.base_log_dir:
                        log_folder = os.path.join(self.base_log_dir, id)
                        os.makedirs(log_folder, exist_ok=True)

                    # Create client instance
                    server_url = f"http://localhost:{port}"
                    client = CodeToolsClient(
                        server_url=server_url,
                        auto_start=True,
                        docker_image=self.docker_image,
                        port=port,
                        log_folder=log_folder,
                        container_name=container_name
                    )

                    # Verify client is working
                    try:
                        status = client.get_status()
                        if not status.get('success'):
                            raise RuntimeError("Client failed to start properly")
                    except Exception as e:
                        # Client failed, clean up and retry
                        logging.warning(f"Client creation failed on port {port}: {e}")
                        client.stop_server()
                        self._used_ports.discard(port)

                        # If this looks like a port issue, try another port
                        if "port" in str(e).lower() or "address already in use" in str(e).lower():
                            if attempt < max_port_retries - 1:
                                continue  # Try next port
                        # Otherwise, it's a server error - fail after retries
                        if attempt >= 2:  # After 3 attempts, give up
                            raise

                    # Store client info
                    self._clients[id] = {
                        'client': client,
                        'port': port,
                        'container_name': container_name,
                        'unique_id': unique_id,
                        'log_folder': log_folder,
                        'created_at': datetime.now().isoformat()
                    }

                    return client

                except RuntimeError as e:
                    # On last attempt, raise the error
                    if attempt == max_port_retries - 1:
                        raise RuntimeError(f"Failed to create client after {max_port_retries} attempts: {e}")
                    # Otherwise continue to next attempt
                    continue

            # Should not reach here, but just in case
            raise RuntimeError(f"Failed to create client for id '{id}'")

    def list_clients(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all managed clients.

        Returns:
            Dictionary mapping client IDs to their metadata
        """
        with self._lock:
            result = {}
            for client_id, info in self._clients.items():
                result[client_id] = {
                    'port': info['port'],
                    'container_name': info['container_name'],
                    'unique_id': info['unique_id'],
                    'log_folder': info['log_folder'],
                    'created_at': info['created_at'],
                    'is_running': self._is_client_running(client_id)
                }
            return result

    def _is_client_running(self, client_id: str) -> bool:
        """Check if a client is currently running."""
        if client_id not in self._clients:
            return False

        client_info = self._clients[client_id]
        client = client_info['client']

        if not client or not hasattr(client, 'docker_container'):
            return False

        try:
            # Try to get status to check if server is responsive
            status = client.get_status()
            return status.get('success', False)
        except Exception:
            return False

    def get_client_info(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific client.

        Args:
            id: Client ID

        Returns:
            Client metadata dictionary or None if not found
        """
        with self._lock:
            if id not in self._clients:
                return None

            info = self._clients[id]
            return {
                'port': info['port'],
                'container_name': info['container_name'],
                'unique_id': info['unique_id'],
                'log_folder': info['log_folder'],
                'created_at': info['created_at'],
                'is_running': self._is_client_running(id)
            }

    def close_client(self, id: str) -> bool:
        """
        Stop and cleanup a specific client.

        Args:
            id: Client ID to stop

        Returns:
            True if successfully stopped, False otherwise
        """
        with self._lock:
            if id not in self._clients:
                logging.warning(f"Client '{id}' not found")
                return False

            client_info = self._clients[id]
            client = client_info['client']
            port = client_info['port']

            success = False
            if client:
                try:
                    # Export logs before stopping
                    if hasattr(client, 'export_logs'):
                        client.export_logs()

                    # Stop the client
                    success = client.stop_server()

                except Exception as e:
                    logging.error(f"Error stopping client '{id}': {e}")

            # Clean up from registry
            del self._clients[id]
            self._used_ports.discard(port)

            return success

    def close_all_clients(self) -> bool:
        """
        Stop and cleanup all managed clients.

        Returns:
            True if all clients stopped successfully, False if any failed
        """
        with self._lock:
            client_ids = list(self._clients.keys())
            all_success = True

            for client_id in client_ids:
                if not self.close_client(client_id):
                    all_success = False
                    logging.error(f"Failed to stop client '{client_id}'")

            return all_success

    # Context Manager Support

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup all clients."""
        self.close_all_clients()
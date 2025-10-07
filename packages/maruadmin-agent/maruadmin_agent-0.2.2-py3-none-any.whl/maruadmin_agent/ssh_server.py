"""
SSH Server implementation using Paramiko
"""
import json
import logging
import os
import socket
import threading
from pathlib import Path
from typing import Any, Dict, Optional

import paramiko


class CommandHandler(paramiko.ServerInterface):
    """SSH command handler"""

    def __init__(self, authorized_keys: list, logger: logging.Logger):
        self.authorized_keys = authorized_keys
        self.logger = logger
        self.event = threading.Event()

    def check_auth_publickey(self, username: str, key: paramiko.PKey) -> int:
        """Check public key authentication"""
        self.logger.info(f"Auth attempt for user: {username}")

        # Get key fingerprint
        key_fingerprint = self.get_key_fingerprint(key)
        self.logger.debug(f"Key fingerprint: {key_fingerprint}")

        # Check against authorized keys
        for auth_key_str in self.authorized_keys:
            try:
                # Parse authorized key
                key_parts = auth_key_str.strip().split()
                if len(key_parts) >= 2:
                    key_type = key_parts[0]
                    key_data = key_parts[1]

                    # Create key object from authorized key
                    if key_type == 'ssh-rsa':
                        auth_key = paramiko.RSAKey(data=paramiko.Message(
                            paramiko.common.decodebytes(key_data.encode())
                        ))
                    elif key_type == 'ssh-ed25519':
                        auth_key = paramiko.Ed25519Key(data=paramiko.Message(
                            paramiko.common.decodebytes(key_data.encode())
                        ))
                    else:
                        continue

                    # Compare keys
                    if key.asbytes() == auth_key.asbytes():
                        self.logger.info(f"Authentication successful for user: {username}")
                        return paramiko.AUTH_SUCCESSFUL

            except Exception as e:
                self.logger.error(f"Error checking key: {e}")
                continue

        self.logger.warning(f"Authentication failed for user: {username}")
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind: str, chanid: int) -> int:
        """Check channel request"""
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command: bytes) -> bool:
        """Handle exec request"""
        self.logger.info(f"Exec request: {command.decode()}")
        self.event.set()
        return True

    def get_key_fingerprint(self, key: paramiko.PKey) -> str:
        """Get key fingerprint"""
        import hashlib
        import base64

        key_bytes = key.asbytes()
        hash_obj = hashlib.sha256(key_bytes)
        fingerprint = base64.b64encode(hash_obj.digest()).decode('utf-8')
        return f"SHA256:{fingerprint.rstrip('=')}"


class SSHServer:
    """SSH Server for agent communication"""

    def __init__(self, config: Any, command_handler: Any, logger: logging.Logger):
        """
        Initialize SSH server

        Args:
            config: Agent configuration
            command_handler: Command handler instance
            logger: Logger instance
        """
        self.config = config
        self.command_handler = command_handler
        self.logger = logger
        self.server_socket = None
        self.server_thread = None
        self.running = False
        self.host_key = None

    def load_or_generate_host_key(self) -> paramiko.PKey:
        """Load or generate SSH host key"""
        host_key_path = Path(self.config.ssh_host_key_path)

        if host_key_path.exists():
            # Load existing key
            self.logger.info(f"Loading host key from {host_key_path}")
            try:
                return paramiko.RSAKey.from_private_key_file(str(host_key_path))
            except Exception as e:
                self.logger.error(f"Failed to load host key: {e}")

        # Generate new key
        self.logger.info("Generating new RSA host key")
        key = paramiko.RSAKey.generate(4096)

        # Save key
        host_key_path.parent.mkdir(parents=True, exist_ok=True)
        key.write_private_key_file(str(host_key_path))
        os.chmod(host_key_path, 0o600)

        # Save public key
        public_key_path = host_key_path.with_suffix('.pub')
        with open(public_key_path, 'w') as f:
            f.write(f"{key.get_name()} {key.get_base64()}\n")

        return key

    def load_authorized_keys(self) -> list:
        """Load authorized keys"""
        authorized_keys = []
        keys_path = Path(self.config.ssh_authorized_keys_path)

        if keys_path.exists():
            self.logger.info(f"Loading authorized keys from {keys_path}")
            with open(keys_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        authorized_keys.append(line)

        self.logger.info(f"Loaded {len(authorized_keys)} authorized keys")
        return authorized_keys

    def handle_client(self, client: socket.socket, addr: tuple) -> None:
        """Handle SSH client connection"""
        self.logger.info(f"Connection from {addr}")

        try:
            # Create SSH transport
            transport = paramiko.Transport(client)
            transport.add_server_key(self.host_key)

            # Load authorized keys
            authorized_keys = self.load_authorized_keys()

            # Create server interface
            server = CommandHandler(authorized_keys, self.logger)
            transport.start_server(server=server)

            # Wait for authentication
            channel = transport.accept(timeout=20)
            if channel is None:
                self.logger.warning("No channel established")
                transport.close()
                return

            self.logger.info("Channel established")

            # Handle commands
            while transport.is_active():
                # Read command
                command_data = channel.recv(4096)
                if not command_data:
                    break

                command_str = command_data.decode('utf-8').strip()
                self.logger.info(f"Received command: {command_str}")

                try:
                    # Parse JSON command
                    command = json.loads(command_str)

                    # Process command
                    response = self.command_handler.handle_command(command)

                    # Send response
                    response_data = json.dumps(response).encode('utf-8')
                    channel.send(response_data + b'\n')

                except json.JSONDecodeError as e:
                    error_response = {
                        'success': False,
                        'error': f'Invalid JSON: {str(e)}'
                    }
                    channel.send(json.dumps(error_response).encode('utf-8') + b'\n')

                except Exception as e:
                    self.logger.error(f"Error handling command: {e}")
                    error_response = {
                        'success': False,
                        'error': str(e)
                    }
                    channel.send(json.dumps(error_response).encode('utf-8') + b'\n')

            channel.close()
            transport.close()

        except Exception as e:
            self.logger.error(f"Error handling client: {e}")

        finally:
            client.close()
            self.logger.info(f"Connection closed from {addr}")

    def run_server(self) -> None:
        """Run SSH server"""
        try:
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config.ssh_host, self.config.ssh_port))
            self.server_socket.listen(5)

            self.logger.info(f"SSH server listening on {self.config.ssh_host}:{self.config.ssh_port}")

            while self.running:
                try:
                    # Accept client connection
                    client, addr = self.server_socket.accept()

                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error accepting connection: {e}")

        except Exception as e:
            self.logger.error(f"SSH server error: {e}")

        finally:
            if self.server_socket:
                self.server_socket.close()
            self.logger.info("SSH server stopped")

    def start(self) -> None:
        """Start SSH server"""
        if self.running:
            return

        # Load host key
        self.host_key = self.load_or_generate_host_key()

        # Start server
        self.running = True
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        self.logger.info("SSH server started")

    def stop(self) -> None:
        """Stop SSH server"""
        if not self.running:
            return

        self.running = False

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.server_socket.close()

        # Wait for server thread
        if self.server_thread:
            self.server_thread.join(timeout=5)

        self.logger.info("SSH server stopped")
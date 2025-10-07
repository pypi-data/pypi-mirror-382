"""
Command handler for processing agent commands
"""
import json
import logging
import subprocess
from datetime import datetime
from typing import Any, Dict, Optional

from .utils import execute_command, get_docker_info, get_system_info


class CommandHandler:
    """Handler for agent commands"""

    def __init__(self, config: Any, logger: logging.Logger):
        """
        Initialize command handler

        Args:
            config: Agent configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

        # Register command handlers
        self.handlers = {
            'ping': self.handle_ping,
            'info': self.handle_info,
            'exec': self.handle_exec,
            'docker': self.handle_docker,
            'service': self.handle_service,
            'file': self.handle_file,
            'update': self.handle_update,
            'restart': self.handle_restart,
            'ssh_key': self.handle_ssh_key,
        }

    def handle_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming command

        Args:
            command: Command dictionary with 'type' and optional 'params'

        Returns:
            Response dictionary
        """
        command_type = command.get('type')
        params = command.get('params', {})

        self.logger.info(f"Processing command: {command_type}")

        # Get handler for command type
        handler = self.handlers.get(command_type)

        if not handler:
            return {
                'success': False,
                'error': f'Unknown command type: {command_type}',
                'timestamp': datetime.utcnow().isoformat()
            }

        try:
            # Execute handler
            result = handler(params)
            result['timestamp'] = datetime.utcnow().isoformat()
            return result

        except Exception as e:
            self.logger.error(f"Error executing command {command_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping command"""
        return {
            'success': True,
            'message': 'pong',
            'agent_id': self.config.agent_id,
            'agent_name': self.config.agent_name
        }

    def handle_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle info command"""
        info_type = params.get('type', 'all')

        if info_type == 'system' or info_type == 'all':
            system_info = get_system_info()
        else:
            system_info = None

        if info_type == 'docker' or info_type == 'all':
            docker_info = get_docker_info()
        else:
            docker_info = None

        return {
            'success': True,
            'system': system_info,
            'docker': docker_info,
            'agent': {
                'id': self.config.agent_id,
                'name': self.config.agent_name,
                'version': '0.1.0',
                'config': {
                    'heartbeat_interval': self.config.heartbeat_interval,
                    'monitor_interval': self.config.monitor_interval,
                    'ssh_port': self.config.ssh_port,
                }
            }
        }

    def handle_exec(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle exec command"""
        command = params.get('command')
        timeout = params.get('timeout', 30)

        if not command:
            return {
                'success': False,
                'error': 'No command specified'
            }

        # Security check - allow only specific commands or patterns
        # In production, implement proper command validation
        allowed_prefixes = [
            'docker', 'systemctl', 'service', 'ls', 'cat', 'grep',
            'ps', 'top', 'df', 'du', 'free', 'netstat', 'ss'
        ]

        command_parts = command.split()
        if not any(command_parts[0].startswith(prefix) for prefix in allowed_prefixes):
            return {
                'success': False,
                'error': f'Command not allowed: {command_parts[0]}'
            }

        # Execute command
        result = execute_command(command, timeout)
        return result

    def handle_docker(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Docker commands"""
        action = params.get('action')

        if action == 'ps':
            # List containers
            result = execute_command('docker ps -a --format json', timeout=10)

            if result['success']:
                containers = []
                for line in result['stdout'].strip().split('\n'):
                    if line:
                        containers.append(json.loads(line))

                return {
                    'success': True,
                    'containers': containers
                }

        elif action == 'images':
            # List images
            result = execute_command('docker images --format json', timeout=10)

            if result['success']:
                images = []
                for line in result['stdout'].strip().split('\n'):
                    if line:
                        images.append(json.loads(line))

                return {
                    'success': True,
                    'images': images
                }

        elif action == 'start':
            container_id = params.get('container_id')
            if not container_id:
                return {'success': False, 'error': 'No container ID specified'}

            result = execute_command(f'docker start {container_id}', timeout=10)
            return result

        elif action == 'stop':
            container_id = params.get('container_id')
            if not container_id:
                return {'success': False, 'error': 'No container ID specified'}

            result = execute_command(f'docker stop {container_id}', timeout=10)
            return result

        elif action == 'restart':
            container_id = params.get('container_id')
            if not container_id:
                return {'success': False, 'error': 'No container ID specified'}

            result = execute_command(f'docker restart {container_id}', timeout=10)
            return result

        elif action == 'logs':
            container_id = params.get('container_id')
            lines = params.get('lines', 100)

            if not container_id:
                return {'success': False, 'error': 'No container ID specified'}

            result = execute_command(f'docker logs --tail {lines} {container_id}', timeout=10)
            return result

        else:
            return {
                'success': False,
                'error': f'Unknown Docker action: {action}'
            }

    def handle_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle service management commands"""
        action = params.get('action')
        service = params.get('service')

        if not service:
            return {
                'success': False,
                'error': 'No service specified'
            }

        # Security check - allow only specific services
        allowed_services = [
            'nginx', 'apache2', 'httpd', 'mysql', 'postgresql',
            'redis', 'docker', 'ssh', 'maruadmin-agent'
        ]

        if service not in allowed_services:
            return {
                'success': False,
                'error': f'Service not allowed: {service}'
            }

        if action == 'status':
            result = execute_command(f'systemctl status {service}', timeout=5)

        elif action == 'start':
            result = execute_command(f'systemctl start {service}', timeout=10)

        elif action == 'stop':
            result = execute_command(f'systemctl stop {service}', timeout=10)

        elif action == 'restart':
            result = execute_command(f'systemctl restart {service}', timeout=10)

        elif action == 'enable':
            result = execute_command(f'systemctl enable {service}', timeout=5)

        elif action == 'disable':
            result = execute_command(f'systemctl disable {service}', timeout=5)

        else:
            return {
                'success': False,
                'error': f'Unknown service action: {action}'
            }

        return result

    def handle_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations"""
        action = params.get('action')
        path = params.get('path')

        if not path:
            return {
                'success': False,
                'error': 'No path specified'
            }

        # Security check - allow only specific paths
        allowed_paths = [
            '/var/log/',
            '/etc/nginx/',
            '/etc/apache2/',
            '/etc/maruadmin/'
        ]

        if not any(path.startswith(prefix) for prefix in allowed_paths):
            return {
                'success': False,
                'error': f'Path not allowed: {path}'
            }

        if action == 'read':
            try:
                with open(path, 'r') as f:
                    content = f.read()

                return {
                    'success': True,
                    'content': content,
                    'path': path
                }

            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }

        elif action == 'write':
            content = params.get('content')
            if content is None:
                return {
                    'success': False,
                    'error': 'No content specified'
                }

            try:
                with open(path, 'w') as f:
                    f.write(content)

                return {
                    'success': True,
                    'path': path
                }

            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }

        else:
            return {
                'success': False,
                'error': f'Unknown file action: {action}'
            }

    def handle_update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent update command"""
        # TODO: Implement agent self-update mechanism
        return {
            'success': False,
            'error': 'Update not implemented yet'
        }

    def handle_restart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent restart command"""
        self.logger.info("Restarting agent...")

        # Schedule restart after response
        import threading

        def restart_agent():
            import time
            time.sleep(2)
            execute_command('systemctl restart maruadmin-agent', timeout=5)

        thread = threading.Thread(target=restart_agent)
        thread.daemon = True
        thread.start()

        return {
            'success': True,
            'message': 'Agent restart scheduled'
        }

    def handle_ssh_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SSH key management commands"""
        action = params.get('action')
        public_key = params.get('public_key')

        if not action:
            return {
                'success': False,
                'error': 'No action specified'
            }

        # Get user from config or use default
        user = params.get('user') or self.config.ssh_user or 'root'

        # Determine authorized_keys path
        if user == 'root':
            authorized_keys_path = '/root/.ssh/authorized_keys'
        else:
            authorized_keys_path = f'/home/{user}/.ssh/authorized_keys'

        if action == 'install':
            if not public_key:
                return {
                    'success': False,
                    'error': 'No public key specified'
                }

            try:
                # Ensure .ssh directory exists
                ssh_dir = authorized_keys_path.rsplit('/', 1)[0]
                execute_command(f'mkdir -p {ssh_dir}', timeout=5)
                execute_command(f'chmod 700 {ssh_dir}', timeout=5)

                # Check if key already exists
                check_result = execute_command(
                    f'grep -F "{public_key}" {authorized_keys_path}',
                    timeout=5
                )

                if check_result['exit_code'] == 0:
                    self.logger.info("SSH key already exists in authorized_keys")
                    return {
                        'success': True,
                        'message': 'SSH key already exists',
                        'path': authorized_keys_path
                    }

                # Append public key to authorized_keys
                result = execute_command(
                    f'echo "{public_key}" >> {authorized_keys_path}',
                    timeout=5
                )

                if result['success']:
                    # Set correct permissions
                    execute_command(f'chmod 600 {authorized_keys_path}', timeout=5)
                    execute_command(f'chown {user}:{user} {authorized_keys_path}', timeout=5)

                    self.logger.info(f"SSH key installed successfully to {authorized_keys_path}")
                    return {
                        'success': True,
                        'message': 'SSH key installed successfully',
                        'path': authorized_keys_path
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Failed to install SSH key: {result.get('stderr', 'Unknown error')}"
                    }

            except Exception as e:
                self.logger.error(f"Error installing SSH key: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        elif action == 'remove':
            if not public_key:
                return {
                    'success': False,
                    'error': 'No public key specified'
                }

            try:
                # Check if authorized_keys exists
                check_file = execute_command(f'test -f {authorized_keys_path}', timeout=5)
                if check_file['exit_code'] != 0:
                    return {
                        'success': True,
                        'message': 'authorized_keys file does not exist'
                    }

                # Create a backup
                execute_command(f'cp {authorized_keys_path} {authorized_keys_path}.bak', timeout=5)

                # Remove the key using sed (escape special characters)
                escaped_key = public_key.replace('/', '\\/')
                result = execute_command(
                    f'sed -i "\\|{escaped_key}|d" {authorized_keys_path}',
                    timeout=5
                )

                if result['success']:
                    self.logger.info(f"SSH key removed successfully from {authorized_keys_path}")
                    return {
                        'success': True,
                        'message': 'SSH key removed successfully',
                        'path': authorized_keys_path
                    }
                else:
                    # Restore backup on failure
                    execute_command(f'mv {authorized_keys_path}.bak {authorized_keys_path}', timeout=5)
                    return {
                        'success': False,
                        'error': f"Failed to remove SSH key: {result.get('stderr', 'Unknown error')}"
                    }

            except Exception as e:
                self.logger.error(f"Error removing SSH key: {e}")
                # Try to restore backup
                execute_command(f'mv {authorized_keys_path}.bak {authorized_keys_path}', timeout=5)
                return {
                    'success': False,
                    'error': str(e)
                }

        elif action == 'list':
            try:
                # Read authorized_keys file
                result = execute_command(f'cat {authorized_keys_path}', timeout=5)

                if result['success']:
                    keys = [line.strip() for line in result['stdout'].split('\n') if line.strip()]
                    return {
                        'success': True,
                        'keys': keys,
                        'count': len(keys),
                        'path': authorized_keys_path
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Failed to read authorized_keys: {result.get('stderr', 'File not found')}"
                    }

            except Exception as e:
                self.logger.error(f"Error listing SSH keys: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        else:
            return {
                'success': False,
                'error': f'Unknown SSH key action: {action}'
            }
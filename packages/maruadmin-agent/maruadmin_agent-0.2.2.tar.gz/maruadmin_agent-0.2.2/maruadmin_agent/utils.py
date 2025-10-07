"""
Utility functions for the agent
"""
import hashlib
import json
import logging
import os
import platform
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def setup_logging(log_file: str, log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration

    Args:
        log_file: Path to log file
        log_level: Logging level

    Returns:
        Logger instance
    """
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger('maruadmin_agent')


def get_system_info() -> Dict[str, Any]:
    """
    Get system information

    Returns:
        Dictionary with system information
    """
    try:
        import psutil

        # Get CPU info
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()

        # Get memory info
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Get disk info
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.mountpoint] = {
                    'device': partition.device,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
            except PermissionError:
                continue

        # Get network info
        network_interfaces = {}
        for interface, addrs in psutil.net_if_addrs().items():
            network_interfaces[interface] = []
            for addr in addrs:
                network_interfaces[interface].append({
                    'family': addr.family.name,
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })

        return {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'os_type': platform.system().lower(),
            'os_version': platform.version(),
            'kernel_version': platform.release(),
            'cpu': {
                'count_physical': cpu_count,
                'count_logical': cpu_count_logical,
                'percent': cpu_percent,
                'frequency_current': cpu_freq.current if cpu_freq else None,
                'frequency_min': cpu_freq.min if cpu_freq else None,
                'frequency_max': cpu_freq.max if cpu_freq else None,
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent,
            },
            'disk': disk_usage,
            'network': network_interfaces,
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'uptime': int(datetime.now().timestamp() - psutil.boot_time())
        }

    except ImportError:
        # Fallback if psutil is not available
        return {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'os_type': platform.system().lower(),
            'os_version': platform.version(),
            'kernel_version': platform.release(),
        }


def get_docker_info() -> Optional[Dict[str, Any]]:
    """
    Get Docker information

    Returns:
        Dictionary with Docker information or None if Docker is not available
    """
    try:
        # Check if Docker is installed
        result = subprocess.run(
            ['docker', 'version', '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return None

        docker_version = json.loads(result.stdout)

        # Get Docker info
        result = subprocess.run(
            ['docker', 'info', '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return None

        docker_info = json.loads(result.stdout)

        # Get container count
        result = subprocess.run(
            ['docker', 'ps', '-a', '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=5
        )

        containers = []
        if result.returncode == 0 and result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    containers.append(json.loads(line))

        return {
            'version': docker_version.get('Client', {}).get('Version'),
            'api_version': docker_version.get('Client', {}).get('ApiVersion'),
            'server_version': docker_version.get('Server', {}).get('Version'),
            'containers_total': len(containers),
            'containers_running': len([c for c in containers if c.get('State') == 'running']),
            'images': docker_info.get('Images', 0),
            'driver': docker_info.get('Driver'),
            'storage_driver': docker_info.get('Driver'),
            'logging_driver': docker_info.get('LoggingDriver'),
            'cgroup_driver': docker_info.get('CgroupDriver'),
            'swarm_active': docker_info.get('Swarm', {}).get('LocalNodeState') == 'active',
            'swarm_node_id': docker_info.get('Swarm', {}).get('NodeID'),
            'swarm_is_manager': docker_info.get('Swarm', {}).get('ControlAvailable', False),
        }

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return None


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, sha512, md5)

    Returns:
        File hash as hexadecimal string
    """
    hash_func = getattr(hashlib, algorithm)()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def execute_command(command: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute a shell command

    Args:
        command: Command to execute
        timeout: Command timeout in seconds

    Returns:
        Dictionary with command result
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            'success': result.returncode == 0,
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'command': command
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'return_code': -1,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'command': command
        }
    except Exception as e:
        return {
            'success': False,
            'return_code': -1,
            'stdout': '',
            'stderr': str(e),
            'command': command
        }


def read_ssh_public_key(key_path: str) -> Optional[str]:
    """
    Read SSH public key from file

    Args:
        key_path: Path to public key file

    Returns:
        Public key content or None if not found
    """
    key_path = Path(key_path)

    # Try common public key file extensions
    for ext in ['', '.pub']:
        pub_key_path = key_path.parent / f"{key_path.stem}{ext}"
        if pub_key_path.exists():
            with open(pub_key_path, 'r') as f:
                return f.read().strip()

    return None


def write_authorized_keys(keys_path: str, public_keys: list) -> None:
    """
    Write authorized keys file

    Args:
        keys_path: Path to authorized_keys file
        public_keys: List of public keys
    """
    keys_path = Path(keys_path)
    keys_path.parent.mkdir(parents=True, exist_ok=True)

    with open(keys_path, 'w') as f:
        for key in public_keys:
            f.write(f"{key}\n")

    # Set proper permissions (600)
    os.chmod(keys_path, 0o600)


def get_agent_id() -> str:
    """
    Generate or retrieve agent ID

    Returns:
        Agent ID
    """
    # Try to get from file
    id_file = Path('/etc/maruadmin/agent.id')

    if id_file.exists():
        with open(id_file, 'r') as f:
            agent_id = f.read().strip()
            if agent_id:
                return agent_id

    # Generate new ID based on system characteristics
    hostname = socket.gethostname()

    # Get MAC address
    import uuid
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                   for elements in range(5, -1, -1)])

    # Create unique ID
    agent_id = hashlib.sha256(f"{hostname}-{mac}".encode()).hexdigest()[:16]

    # Save to file
    id_file.parent.mkdir(parents=True, exist_ok=True)
    with open(id_file, 'w') as f:
        f.write(agent_id)

    return agent_id
"""
Agent configuration management
"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AgentConfig:
    """Agent configuration"""

    # Server settings
    agent_id: Optional[str] = None
    agent_name: str = "maruadmin-agent"
    api_url: str = "http://localhost:8000"
    api_token: Optional[str] = None

    # SSH server settings
    ssh_host: str = "0.0.0.0"
    ssh_port: int = 2222
    ssh_host_key_path: str = "/etc/maruadmin/ssh_host_key"
    ssh_authorized_keys_path: str = "/etc/maruadmin/authorized_keys"

    # Heartbeat settings
    heartbeat_interval: int = 30  # seconds
    heartbeat_timeout: int = 5  # seconds

    # System monitoring
    monitor_interval: int = 60  # seconds
    monitor_cpu: bool = True
    monitor_memory: bool = True
    monitor_disk: bool = True
    monitor_network: bool = True
    monitor_docker: bool = True

    # Logging
    log_level: str = "INFO"
    log_file: str = "/var/log/maruadmin/agent.log"
    log_max_size: int = 10  # MB
    log_backup_count: int = 5

    # Paths
    config_dir: str = "/etc/maruadmin"
    data_dir: str = "/var/lib/maruadmin"
    run_dir: str = "/var/run/maruadmin"

    # Security
    enable_tls: bool = False
    tls_cert_path: Optional[str] = None
    tls_key_path: Optional[str] = None
    tls_ca_path: Optional[str] = None

    # Features
    enable_docker: bool = True
    enable_systemd: bool = True
    enable_firewall: bool = False

    @classmethod
    def from_file(cls, config_path: str) -> "AgentConfig":
        """Load configuration from file"""
        path = Path(config_path)

        if not path.exists():
            return cls()

        with open(path, 'r') as f:
            if path.suffix == '.json':
                data = json.load(f)
            else:
                # Assume it's a simple key=value format
                data = {}
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip().lower()
                            value = value.strip()

                            # Convert to appropriate type
                            if value.lower() in ('true', 'false'):
                                value = value.lower() == 'true'
                            elif value.isdigit():
                                value = int(value)

                            data[key] = value

        return cls(**data)

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables"""
        config = cls()

        # Map environment variables to config fields
        env_mapping = {
            'MARUADMIN_AGENT_ID': 'agent_id',
            'MARUADMIN_AGENT_NAME': 'agent_name',
            'MARUADMIN_API_URL': 'api_url',
            'MARUADMIN_API_TOKEN': 'api_token',
            'MARUADMIN_SSH_HOST': 'ssh_host',
            'MARUADMIN_SSH_PORT': 'ssh_port',
            'MARUADMIN_SSH_HOST_KEY': 'ssh_host_key_path',
            'MARUADMIN_SSH_AUTHORIZED_KEYS': 'ssh_authorized_keys_path',
            'MARUADMIN_HEARTBEAT_INTERVAL': 'heartbeat_interval',
            'MARUADMIN_HEARTBEAT_TIMEOUT': 'heartbeat_timeout',
            'MARUADMIN_MONITOR_INTERVAL': 'monitor_interval',
            'MARUADMIN_LOG_LEVEL': 'log_level',
            'MARUADMIN_LOG_FILE': 'log_file',
            'MARUADMIN_CONFIG_DIR': 'config_dir',
            'MARUADMIN_DATA_DIR': 'data_dir',
            'MARUADMIN_RUN_DIR': 'run_dir',
            'MARUADMIN_ENABLE_TLS': 'enable_tls',
            'MARUADMIN_TLS_CERT': 'tls_cert_path',
            'MARUADMIN_TLS_KEY': 'tls_key_path',
            'MARUADMIN_TLS_CA': 'tls_ca_path',
        }

        for env_var, field_name in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Convert to appropriate type
                field_type = type(getattr(config, field_name))
                if field_type == bool:
                    value = value.lower() in ('true', '1', 'yes')
                elif field_type == int:
                    value = int(value)

                setattr(config, field_name, value)

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'api_url': self.api_url,
            'ssh_host': self.ssh_host,
            'ssh_port': self.ssh_port,
            'heartbeat_interval': self.heartbeat_interval,
            'monitor_interval': self.monitor_interval,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'enable_docker': self.enable_docker,
            'enable_systemd': self.enable_systemd,
            'enable_firewall': self.enable_firewall,
        }

    def save(self, config_path: str) -> None:
        """Save configuration to file"""
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        for dir_path in [self.config_dir, self.data_dir, self.run_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

        # Ensure log directory exists
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = None


def load_config(config_path: Optional[str] = None) -> AgentConfig:
    """Load configuration from file or environment"""
    global config

    if config_path and Path(config_path).exists():
        config = AgentConfig.from_file(config_path)
    else:
        # Try to load from environment first, then default locations
        config = AgentConfig.from_env()

        # Try default config locations
        default_paths = [
            '/etc/maruadmin/agent.conf',
            '/etc/maruadmin/agent.json',
            './agent.conf',
            './agent.json',
        ]

        for path in default_paths:
            if Path(path).exists():
                file_config = AgentConfig.from_file(path)
                # Merge with env config (env takes precedence)
                for key, value in file_config.__dict__.items():
                    if getattr(config, key) is None:
                        setattr(config, key, value)
                break

    config.ensure_directories()
    return config


def get_config() -> AgentConfig:
    """Get current configuration"""
    global config
    if config is None:
        config = load_config()
    return config
"""
System monitoring module
"""
import json
import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from .metrics_collector import MetricsCollector
from .utils import get_docker_info, get_system_info


class SystemMonitor:
    """System monitoring and heartbeat service"""

    def __init__(self, config: Any, logger: logging.Logger):
        """
        Initialize system monitor

        Args:
            config: Agent configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.running = False
        self.heartbeat_thread = None
        self.monitor_thread = None
        self.last_metrics = {}
        self.metrics_collector = MetricsCollector()

    def send_heartbeat(self) -> bool:
        """
        Send heartbeat to server

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare heartbeat data
            data = {
                'agent_id': self.config.agent_id,
                'agent_name': self.config.agent_name,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'online'
            }

            # Send heartbeat
            headers = {
                'Content-Type': 'application/json'
            }

            if self.config.api_token:
                headers['Authorization'] = f'Bearer {self.config.api_token}'

            response = requests.post(
                f"{self.config.api_url}/api/v1/agents/heartbeat",
                json=data,
                headers=headers,
                timeout=self.config.heartbeat_timeout
            )

            if response.status_code == 200:
                self.logger.debug("Heartbeat sent successfully")
                return True
            else:
                self.logger.warning(f"Heartbeat failed with status: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            self.logger.warning("Heartbeat timeout")
            return False

        except requests.exceptions.ConnectionError:
            self.logger.warning("Cannot connect to server")
            return False

        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")
            return False

    def send_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Send system metrics to server

        Args:
            metrics: System metrics dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare metrics data
            data = {
                'agent_id': self.config.agent_id,
                'agent_name': self.config.agent_name,
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': metrics
            }

            # Send metrics
            headers = {
                'Content-Type': 'application/json'
            }

            if self.config.api_token:
                headers['Authorization'] = f'Bearer {self.config.api_token}'

            response = requests.post(
                f"{self.config.api_url}/api/v1/agents/metrics",
                json=data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.debug("Metrics sent successfully")
                return True
            else:
                self.logger.warning(f"Metrics failed with status: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Metrics error: {e}")
            return False

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect system metrics using the enhanced metrics collector

        Returns:
            Dictionary with system metrics
        """
        try:
            # Use the new comprehensive metrics collector
            metrics = self.metrics_collector.collect_all_metrics()

            # Add Docker info if enabled
            if self.config.monitor_docker and self.config.enable_docker:
                docker_info = get_docker_info()
                if docker_info:
                    metrics['docker'] = {
                        'version': docker_info['version'],
                        'containers_total': docker_info['containers_total'],
                        'containers_running': docker_info['containers_running'],
                        'images': docker_info['images']
                    }

            self.last_metrics = metrics
            return metrics

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return self.last_metrics

    def heartbeat_loop(self) -> None:
        """Heartbeat loop"""
        self.logger.info("Starting heartbeat loop")

        while self.running:
            try:
                # Send heartbeat
                self.send_heartbeat()

                # Wait for next interval
                time.sleep(self.config.heartbeat_interval)

            except Exception as e:
                self.logger.error(f"Heartbeat loop error: {e}")
                time.sleep(self.config.heartbeat_interval)

        self.logger.info("Heartbeat loop stopped")

    def monitor_loop(self) -> None:
        """Monitoring loop"""
        self.logger.info("Starting monitor loop")

        while self.running:
            try:
                # Collect metrics
                metrics = self.collect_metrics()

                # Send metrics
                if metrics:
                    self.send_metrics(metrics)

                # Wait for next interval
                time.sleep(self.config.monitor_interval)

            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(self.config.monitor_interval)

        self.logger.info("Monitor loop stopped")

    def start(self) -> None:
        """Start monitoring"""
        if self.running:
            return

        self.running = True

        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.logger.info("System monitoring started")

    def stop(self) -> None:
        """Stop monitoring"""
        if not self.running:
            return

        self.running = False

        # Wait for threads to stop
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.logger.info("System monitoring stopped")

    def get_status(self) -> Dict[str, Any]:
        """
        Get monitoring status

        Returns:
            Status dictionary
        """
        return {
            'running': self.running,
            'heartbeat_interval': self.config.heartbeat_interval,
            'monitor_interval': self.config.monitor_interval,
            'last_metrics': self.last_metrics
        }


class AgentRegistration:
    """Agent registration service"""

    @staticmethod
    def register_agent(config: Any, logger: logging.Logger) -> bool:
        """
        Register agent with server

        Args:
            config: Agent configuration
            logger: Logger instance

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get system info
            system_info = get_system_info()
            docker_info = get_docker_info()

            # Read SSH public key
            from pathlib import Path
            ssh_public_key = None
            host_key_path = Path(config.ssh_host_key_path)
            pub_key_path = host_key_path.with_suffix('.pub')

            if pub_key_path.exists():
                with open(pub_key_path, 'r') as f:
                    ssh_public_key = f.read().strip()

            # Prepare registration data
            data = {
                'agent_id': config.agent_id,
                'name': config.agent_name,
                'hostname': system_info.get('hostname'),
                'ip_address': get_local_ip(),
                'ssh_port': config.ssh_port,
                'ssh_public_key': ssh_public_key,
                'os_type': system_info.get('os_type'),
                'os_version': system_info.get('os_version'),
                'kernel_version': system_info.get('kernel_version'),
                'cpu_cores': system_info.get('cpu', {}).get('count_logical'),
                'memory_total': system_info.get('memory', {}).get('total'),
                'docker_version': docker_info.get('version') if docker_info else None,
                'capabilities': {
                    'docker': config.enable_docker and docker_info is not None,
                    'systemd': config.enable_systemd,
                    'firewall': config.enable_firewall
                }
            }

            # Send registration request
            headers = {
                'Content-Type': 'application/json'
            }

            if config.api_token:
                headers['Authorization'] = f'Bearer {config.api_token}'

            response = requests.post(
                f"{config.api_url}/api/v1/agents/register",
                json=data,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                logger.info("Agent registered successfully")

                # Update configuration with server response
                result = response.json()
                if 'agent_id' in result:
                    config.agent_id = result['agent_id']

                # Download authorized keys
                if 'authorized_keys' in result:
                    from .utils import write_authorized_keys
                    write_authorized_keys(
                        config.ssh_authorized_keys_path,
                        result['authorized_keys']
                    )

                return True

            else:
                logger.error(f"Registration failed with status: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False


def get_local_ip() -> str:
    """Get local IP address"""
    import socket
    try:
        # Connect to a public DNS to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
"""
Docker management module for MaruAdmin agent.
"""

import docker
import logging
from typing import Dict, List, Optional, Any
import json
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class DockerManager:
    """Manage Docker containers and integration with HAProxy on the agent."""

    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None

    def install_docker(self) -> Dict[str, Any]:
        """
        Install Docker if not already installed.

        Returns:
            Installation status
        """
        try:
            # Check if Docker is installed
            result = subprocess.run(
                ["which", "docker"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Docker is already installed"
                }

            # Install Docker
            install_commands = [
                ["apt-get", "update"],
                ["apt-get", "install", "-y", "ca-certificates", "curl", "gnupg", "lsb-release"],
                ["mkdir", "-p", "/etc/apt/keyrings"],
            ]

            for cmd in install_commands:
                subprocess.run(cmd, check=False)

            # Add Docker's official GPG key
            subprocess.run(
                "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
                shell=True,
                check=False
            )

            # Set up the repository
            subprocess.run(
                'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] '
                'https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | '
                'tee /etc/apt/sources.list.d/docker.list > /dev/null',
                shell=True,
                check=False
            )

            # Install Docker Engine
            install_result = subprocess.run(
                ["apt-get", "update"],
                check=False
            )

            install_result = subprocess.run(
                ["apt-get", "install", "-y", "docker-ce", "docker-ce-cli", "containerd.io",
                 "docker-compose-plugin"],
                capture_output=True,
                text=True,
                check=False
            )

            if install_result.returncode == 0:
                # Enable and start Docker service
                subprocess.run(["systemctl", "enable", "docker"], check=False)
                subprocess.run(["systemctl", "start", "docker"], check=False)

                # Reinitialize client
                self.client = docker.from_env()

                return {
                    "status": "success",
                    "message": "Docker installed successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to install Docker: {install_result.stderr}"
                }

        except Exception as e:
            logger.error(f"Failed to install Docker: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def list_containers(self, all_containers: bool = False) -> Dict[str, Any]:
        """
        List Docker containers.

        Args:
            all_containers: Include stopped containers

        Returns:
            List of containers
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker client not initialized"
            }

        try:
            containers = self.client.containers.list(all=all_containers)
            container_list = []

            for container in containers:
                container_info = {
                    "id": container.short_id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else container.image.short_id,
                    "status": container.status,
                    "created": container.attrs['Created'],
                    "ports": self._parse_ports(container.attrs['NetworkSettings']['Ports']),
                    "labels": container.labels,
                    "environment": container.attrs['Config'].get('Env', [])
                }
                container_list.append(container_info)

            return {
                "status": "success",
                "containers": container_list
            }

        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _parse_ports(self, ports_config: Dict) -> List[Dict[str, Any]]:
        """Parse Docker container ports configuration."""
        ports = []
        if not ports_config:
            return ports

        for container_port, host_config in ports_config.items():
            if host_config:
                for binding in host_config:
                    ports.append({
                        "container": container_port,
                        "host": f"{binding['HostIp']}:{binding['HostPort']}"
                    })

        return ports

    def create_container(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Docker container.

        Args:
            config: Container configuration

        Returns:
            Container creation status
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker client not initialized"
            }

        try:
            # Extract configuration
            name = config.get("name")
            image = config.get("image")
            environment = config.get("environment", {})
            ports = config.get("ports", {})
            volumes = config.get("volumes", {})
            networks = config.get("networks", [])
            labels = config.get("labels", {})

            # Pull image if not exists
            try:
                self.client.images.get(image)
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling image {image}")
                self.client.images.pull(image)

            # Create container
            container = self.client.containers.run(
                image=image,
                name=name,
                detach=True,
                environment=environment,
                ports=ports,
                volumes=volumes,
                labels=labels
            )

            # Attach to networks
            for network in networks:
                if network and network != "bridge":
                    try:
                        net = self.client.networks.get(network)
                        net.connect(container)
                    except Exception as e:
                        logger.warning(f"Failed to connect to network {network}: {e}")

            return {
                "status": "success",
                "container_id": container.short_id,
                "message": f"Container {name} created successfully"
            }

        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def start_container(self, container_id: str) -> Dict[str, Any]:
        """
        Start a Docker container.

        Args:
            container_id: Container ID or name

        Returns:
            Operation status
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker client not initialized"
            }

        try:
            container = self.client.containers.get(container_id)
            container.start()

            return {
                "status": "success",
                "message": f"Container {container_id} started"
            }

        except docker.errors.NotFound:
            return {
                "status": "error",
                "message": f"Container {container_id} not found"
            }
        except Exception as e:
            logger.error(f"Failed to start container {container_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def stop_container(self, container_id: str) -> Dict[str, Any]:
        """
        Stop a Docker container.

        Args:
            container_id: Container ID or name

        Returns:
            Operation status
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker client not initialized"
            }

        try:
            container = self.client.containers.get(container_id)
            container.stop()

            return {
                "status": "success",
                "message": f"Container {container_id} stopped"
            }

        except docker.errors.NotFound:
            return {
                "status": "error",
                "message": f"Container {container_id} not found"
            }
        except Exception as e:
            logger.error(f"Failed to stop container {container_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def restart_container(self, container_id: str) -> Dict[str, Any]:
        """
        Restart a Docker container.

        Args:
            container_id: Container ID or name

        Returns:
            Operation status
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker client not initialized"
            }

        try:
            container = self.client.containers.get(container_id)
            container.restart()

            return {
                "status": "success",
                "message": f"Container {container_id} restarted"
            }

        except docker.errors.NotFound:
            return {
                "status": "error",
                "message": f"Container {container_id} not found"
            }
        except Exception as e:
            logger.error(f"Failed to restart container {container_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def remove_container(self, container_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Remove a Docker container.

        Args:
            container_id: Container ID or name
            force: Force removal even if running

        Returns:
            Operation status
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker client not initialized"
            }

        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)

            return {
                "status": "success",
                "message": f"Container {container_id} removed"
            }

        except docker.errors.NotFound:
            return {
                "status": "error",
                "message": f"Container {container_id} not found"
            }
        except Exception as e:
            logger.error(f"Failed to remove container {container_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def get_container_logs(self, container_id: str, lines: int = 100) -> Dict[str, Any]:
        """
        Get container logs.

        Args:
            container_id: Container ID or name
            lines: Number of lines to retrieve

        Returns:
            Container logs
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker client not initialized"
            }

        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=lines, timestamps=True).decode('utf-8')

            return {
                "status": "success",
                "logs": logs
            }

        except docker.errors.NotFound:
            return {
                "status": "error",
                "message": f"Container {container_id} not found"
            }
        except Exception as e:
            logger.error(f"Failed to get logs for container {container_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """
        Get container resource usage statistics.

        Args:
            container_id: Container ID or name

        Returns:
            Container statistics
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker client not initialized"
            }

        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)

            # Calculate useful metrics
            cpu_percent = self._calculate_cpu_percentage(stats)
            memory_usage = self._calculate_memory_usage(stats)
            network_io = self._calculate_network_io(stats)

            return {
                "status": "success",
                "stats": {
                    "cpu_percent": cpu_percent,
                    "memory": memory_usage,
                    "network": network_io
                }
            }

        except docker.errors.NotFound:
            return {
                "status": "error",
                "message": f"Container {container_id} not found"
            }
        except Exception as e:
            logger.error(f"Failed to get stats for container {container_id}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _calculate_cpu_percentage(self, stats: Dict) -> float:
        """Calculate CPU usage percentage."""
        try:
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                       stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                          stats["precpu_stats"]["system_cpu_usage"]

            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * 100.0
                return round(cpu_percent, 2)

            return 0.0
        except Exception:
            return 0.0

    def _calculate_memory_usage(self, stats: Dict) -> Dict[str, Any]:
        """Calculate memory usage."""
        try:
            memory_usage = stats["memory_stats"]["usage"]
            memory_limit = stats["memory_stats"]["limit"]

            if memory_limit > 0:
                memory_percent = (memory_usage / memory_limit) * 100.0
                return {
                    "usage_mb": round(memory_usage / (1024 * 1024), 2),
                    "limit_mb": round(memory_limit / (1024 * 1024), 2),
                    "percent": round(memory_percent, 2)
                }

            return {
                "usage_mb": round(memory_usage / (1024 * 1024), 2),
                "limit_mb": 0,
                "percent": 0.0
            }
        except Exception:
            return {
                "usage_mb": 0,
                "limit_mb": 0,
                "percent": 0.0
            }

    def _calculate_network_io(self, stats: Dict) -> Dict[str, Any]:
        """Calculate network I/O."""
        try:
            networks = stats.get("networks", {})
            total_rx = 0
            total_tx = 0

            for interface, data in networks.items():
                total_rx += data.get("rx_bytes", 0)
                total_tx += data.get("tx_bytes", 0)

            return {
                "rx_mb": round(total_rx / (1024 * 1024), 2),
                "tx_mb": round(total_tx / (1024 * 1024), 2)
            }
        except Exception:
            return {
                "rx_mb": 0,
                "tx_mb": 0
            }

    def cleanup_unused(self) -> Dict[str, Any]:
        """
        Clean up unused Docker resources.

        Returns:
            Cleanup status
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker client not initialized"
            }

        try:
            # Prune containers
            containers_result = self.client.containers.prune()

            # Prune images
            images_result = self.client.images.prune()

            # Prune volumes
            volumes_result = self.client.volumes.prune()

            # Prune networks
            networks_result = self.client.networks.prune()

            return {
                "status": "success",
                "message": "Docker cleanup completed",
                "details": {
                    "containers_removed": len(containers_result.get("ContainersDeleted", [])),
                    "images_removed": len(images_result.get("ImagesDeleted", [])),
                    "volumes_removed": len(volumes_result.get("VolumesDeleted", [])),
                    "networks_removed": len(networks_result.get("NetworksDeleted", []))
                }
            }

        except Exception as e:
            logger.error(f"Failed to cleanup Docker resources: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
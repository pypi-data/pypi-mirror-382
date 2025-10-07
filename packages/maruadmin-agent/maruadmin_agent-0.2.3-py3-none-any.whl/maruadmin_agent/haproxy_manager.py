"""
HAProxy management module for MaruAdmin agent.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import tempfile
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


class HAProxyManager:
    """Manage HAProxy configuration and operations on the agent."""

    def __init__(self):
        self.config_dir = Path("/etc/haproxy")
        self.certs_dir = self.config_dir / "certs"
        self.config_file = self.config_dir / "haproxy.cfg"
        self.domain_map_file = self.config_dir / "domain.map"
        self.backup_dir = self.config_dir / "backups"

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        for directory in [self.config_dir, self.certs_dir, self.backup_dir]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Ensured directory exists: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")

    def install_haproxy(self) -> Dict[str, Any]:
        """
        Install HAProxy if not already installed.

        Returns:
            Installation status
        """
        try:
            # Check if HAProxy is installed
            result = subprocess.run(
                ["which", "haproxy"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "HAProxy is already installed"
                }

            # Install HAProxy
            install_result = subprocess.run(
                ["apt-get", "install", "-y", "haproxy"],
                capture_output=True,
                text=True,
                check=False
            )

            if install_result.returncode == 0:
                # Enable HAProxy service
                subprocess.run(
                    ["systemctl", "enable", "haproxy"],
                    check=False
                )

                return {
                    "status": "success",
                    "message": "HAProxy installed successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to install HAProxy: {install_result.stderr}"
                }

        except Exception as e:
            logger.error(f"Failed to install HAProxy: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def update_configuration(self, config: str, domain_map: str) -> Dict[str, Any]:
        """
        Update HAProxy configuration files.

        Args:
            config: HAProxy configuration content
            domain_map: Domain mapping content

        Returns:
            Update status
        """
        try:
            # Backup current configuration
            self._backup_configuration()

            # Write new configuration to temporary files
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cfg') as temp_config:
                temp_config.write(config)
                temp_config_path = temp_config.name

            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.map') as temp_map:
                temp_map.write(domain_map)
                temp_map_path = temp_map.name

            # Validate configuration
            validation_result = self._validate_config(temp_config_path)

            if validation_result["valid"]:
                # Move temporary files to actual locations
                shutil.move(temp_config_path, str(self.config_file))
                shutil.move(temp_map_path, str(self.domain_map_file))

                # Set proper permissions
                os.chmod(self.config_file, 0o644)
                os.chmod(self.domain_map_file, 0o644)

                return {
                    "status": "success",
                    "message": "Configuration updated successfully"
                }
            else:
                # Clean up temporary files
                os.unlink(temp_config_path)
                os.unlink(temp_map_path)

                return {
                    "status": "error",
                    "message": f"Configuration validation failed: {validation_result['error']}"
                }

        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _backup_configuration(self) -> None:
        """Backup current HAProxy configuration."""
        try:
            if self.config_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_dir / f"haproxy_{timestamp}.cfg"
                shutil.copy2(self.config_file, backup_file)
                logger.info(f"Configuration backed up to {backup_file}")

                # Keep only last 10 backups
                backups = sorted(self.backup_dir.glob("haproxy_*.cfg"))
                if len(backups) > 10:
                    for old_backup in backups[:-10]:
                        old_backup.unlink()
                        logger.info(f"Removed old backup: {old_backup}")

        except Exception as e:
            logger.error(f"Failed to backup configuration: {e}")

    def _validate_config(self, config_path: str) -> Dict[str, Any]:
        """
        Validate HAProxy configuration.

        Args:
            config_path: Path to configuration file

        Returns:
            Validation result
        """
        try:
            result = subprocess.run(
                ["haproxy", "-c", "-f", config_path],
                capture_output=True,
                text=True,
                check=False
            )

            return {
                "valid": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None
            }

        except Exception as e:
            logger.error(f"Failed to validate configuration: {e}")
            return {
                "valid": False,
                "error": str(e)
            }

    def reload_service(self) -> Dict[str, Any]:
        """
        Reload HAProxy service.

        Returns:
            Reload status
        """
        try:
            result = subprocess.run(
                ["systemctl", "reload", "haproxy"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "HAProxy reloaded successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to reload HAProxy: {result.stderr}"
                }

        except Exception as e:
            logger.error(f"Failed to reload HAProxy: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def restart_service(self) -> Dict[str, Any]:
        """
        Restart HAProxy service.

        Returns:
            Restart status
        """
        try:
            result = subprocess.run(
                ["systemctl", "restart", "haproxy"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "HAProxy restarted successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to restart HAProxy: {result.stderr}"
                }

        except Exception as e:
            logger.error(f"Failed to restart HAProxy: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get HAProxy service status.

        Returns:
            Service status information
        """
        try:
            result = subprocess.run(
                ["systemctl", "status", "haproxy"],
                capture_output=True,
                text=True,
                check=False
            )

            is_active = "active (running)" in result.stdout

            return {
                "status": "success",
                "active": is_active,
                "service_status": "running" if is_active else "stopped",
                "output": result.stdout
            }

        except Exception as e:
            logger.error(f"Failed to get HAProxy status: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def add_certificate(self, domain: str, cert_content: str, key_content: str) -> Dict[str, Any]:
        """
        Add SSL certificate for a domain.

        Args:
            domain: Domain name
            cert_content: Certificate content
            key_content: Private key content

        Returns:
            Operation status
        """
        try:
            # HAProxy expects certificates in PEM format with key and cert combined
            pem_file = self.certs_dir / f"{domain}.pem"

            # Combine key and certificate
            with open(pem_file, 'w') as pem:
                pem.write(key_content)
                pem.write("\n")
                pem.write(cert_content)

            # Set proper permissions
            os.chmod(pem_file, 0o600)

            logger.info(f"Added certificate for {domain}")

            return {
                "status": "success",
                "message": f"Certificate added for {domain}"
            }

        except Exception as e:
            logger.error(f"Failed to add certificate for {domain}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def remove_certificate(self, domain: str) -> Dict[str, Any]:
        """
        Remove SSL certificate for a domain.

        Args:
            domain: Domain name

        Returns:
            Operation status
        """
        try:
            pem_file = self.certs_dir / f"{domain}.pem"

            if pem_file.exists():
                pem_file.unlink()
                logger.info(f"Removed certificate for {domain}")

                return {
                    "status": "success",
                    "message": f"Certificate removed for {domain}"
                }
            else:
                return {
                    "status": "warning",
                    "message": f"Certificate for {domain} not found"
                }

        except Exception as e:
            logger.error(f"Failed to remove certificate for {domain}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get HAProxy statistics.

        Returns:
            HAProxy statistics
        """
        try:
            # Use HAProxy stats socket to get statistics
            result = subprocess.run(
                "echo 'show stat' | socat stdio /run/haproxy/admin.sock",
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                # Parse CSV output
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    headers = lines[0].replace('# ', '').split(',')
                    stats = []

                    for line in lines[1:]:
                        values = line.split(',')
                        if len(values) == len(headers):
                            stat_dict = dict(zip(headers, values))
                            stats.append(stat_dict)

                    return {
                        "status": "success",
                        "stats": stats
                    }

            return {
                "status": "warning",
                "message": "No statistics available"
            }

        except Exception as e:
            logger.error(f"Failed to get HAProxy statistics: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def sync_letsencrypt_certificates(self) -> Dict[str, Any]:
        """
        Sync Let's Encrypt certificates with HAProxy.

        Returns:
            Sync status
        """
        try:
            letsencrypt_dir = Path("/etc/letsencrypt/live")
            if not letsencrypt_dir.exists():
                return {
                    "status": "warning",
                    "message": "Let's Encrypt directory not found"
                }

            synced_domains = []

            for domain_dir in letsencrypt_dir.iterdir():
                if domain_dir.is_dir():
                    domain = domain_dir.name
                    cert_file = domain_dir / "fullchain.pem"
                    key_file = domain_dir / "privkey.pem"

                    if cert_file.exists() and key_file.exists():
                        # Read certificate and key
                        with open(cert_file, 'r') as f:
                            cert_content = f.read()
                        with open(key_file, 'r') as f:
                            key_content = f.read()

                        # Add to HAProxy
                        result = self.add_certificate(domain, cert_content, key_content)
                        if result["status"] == "success":
                            synced_domains.append(domain)

            if synced_domains:
                return {
                    "status": "success",
                    "message": f"Synced certificates for: {', '.join(synced_domains)}"
                }
            else:
                return {
                    "status": "warning",
                    "message": "No certificates found to sync"
                }

        except Exception as e:
            logger.error(f"Failed to sync Let's Encrypt certificates: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
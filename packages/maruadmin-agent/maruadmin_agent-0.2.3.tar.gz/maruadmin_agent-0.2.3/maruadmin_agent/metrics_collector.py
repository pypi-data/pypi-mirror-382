"""
System metrics collector for MaruAdmin agent
"""
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

try:
    import psutil
except ImportError:
    print("psutil is required. Install it with: pip install psutil")
    raise


logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects system metrics using psutil"""

    def __init__(self):
        """Initialize the metrics collector"""
        self.last_network_io = None
        self.last_disk_io = None
        self.last_collection_time = None

    def collect_cpu_metrics(self) -> Dict[str, Any]:
        """Collect CPU metrics"""
        try:
            # Get CPU usage with 1 second interval for accurate measurement
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None

            metrics = {
                'usage_percent': cpu_percent,
                'cores': cpu_count,
                'frequency': cpu_freq.current if cpu_freq else None,
                'temperature': self._get_cpu_temperature(),
                'load_average': {
                    '1m': load_avg[0] if load_avg else None,
                    '5m': load_avg[1] if load_avg else None,
                    '15m': load_avg[2] if load_avg else None
                } if load_avg else None
            }

            return metrics
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
            return {
                'usage_percent': 0.0,
                'cores': 1,
                'frequency': None,
                'temperature': None,
                'load_average': None
            }

    def collect_memory_metrics(self) -> Dict[str, Any]:
        """Collect memory metrics"""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            metrics = {
                'total': mem.total // (1024 * 1024),  # Convert to MB
                'used': mem.used // (1024 * 1024),
                'available': mem.available // (1024 * 1024),
                'percent': mem.percent,
                'swap_total': swap.total // (1024 * 1024) if swap else None,
                'swap_used': swap.used // (1024 * 1024) if swap else None,
                'swap_percent': swap.percent if swap else None
            }

            return metrics
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
            return {
                'total': 0,
                'used': 0,
                'available': 0,
                'percent': 0.0
            }

    def collect_disk_metrics(self) -> Dict[str, Any]:
        """Collect disk metrics"""
        try:
            # Get main disk usage
            disk = psutil.disk_usage('/')

            # Collect partition information
            partitions = []
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    partitions.append({
                        'device': part.device,
                        'mountpoint': part.mountpoint,
                        'fstype': part.fstype,
                        'total': usage.total // (1024 * 1024 * 1024),  # GB
                        'used': usage.used // (1024 * 1024 * 1024),
                        'free': usage.free // (1024 * 1024 * 1024),
                        'percent': usage.percent
                    })
                except PermissionError:
                    continue

            metrics = {
                'total': disk.total / (1024 * 1024 * 1024),  # Convert to GB
                'used': disk.used / (1024 * 1024 * 1024),
                'free': disk.free / (1024 * 1024 * 1024),
                'percent': disk.percent,
                'partitions': partitions
            }

            # Get disk I/O stats if available
            if hasattr(psutil, 'disk_io_counters'):
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    metrics['io_read_bytes'] = disk_io.read_bytes
                    metrics['io_write_bytes'] = disk_io.write_bytes

            return metrics
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
            return {
                'total': 0.0,
                'used': 0.0,
                'free': 0.0,
                'percent': 0.0,
                'partitions': []
            }

    def collect_network_metrics(self) -> Dict[str, Any]:
        """Collect network metrics"""
        try:
            # Get network I/O stats
            net_io = psutil.net_io_counters()

            # Get network connections count
            try:
                connections = len(psutil.net_connections())
            except:
                connections = None

            # Get network interfaces
            interfaces = []
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()

            for iface_name, addrs in net_if_addrs.items():
                stats = net_if_stats.get(iface_name)
                iface_info = {
                    'name': iface_name,
                    'is_up': stats.isup if stats else False,
                    'speed': stats.speed if stats else None,
                    'addresses': []
                }

                for addr in addrs:
                    iface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })

                interfaces.append(iface_info)

            metrics = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
                'connections': connections,
                'interfaces': interfaces
            }

            # Calculate bandwidth if we have previous measurements
            if self.last_network_io and self.last_collection_time:
                time_diff = time.time() - self.last_collection_time
                if time_diff > 0:
                    metrics['bandwidth_sent'] = (net_io.bytes_sent - self.last_network_io.bytes_sent) / time_diff
                    metrics['bandwidth_recv'] = (net_io.bytes_recv - self.last_network_io.bytes_recv) / time_diff

            self.last_network_io = net_io

            return metrics
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
            return {
                'bytes_sent': None,
                'bytes_recv': None,
                'packets_sent': None,
                'packets_recv': None,
                'errors_in': None,
                'errors_out': None,
                'connections': None,
                'interfaces': []
            }

    def collect_process_metrics(self) -> Dict[str, Any]:
        """Collect process metrics"""
        try:
            processes = list(psutil.process_iter(['pid', 'name', 'status']))

            # Count processes by status
            status_count = {}
            thread_count = 0

            for proc in processes:
                try:
                    status = proc.info['status']
                    status_count[status] = status_count.get(status, 0) + 1
                    thread_count += proc.num_threads()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            metrics = {
                'count': len(processes),
                'threads': thread_count,
                'by_status': status_count
            }

            # Get top processes by CPU and memory
            top_cpu = []
            top_mem = []

            for proc in processes[:10]:  # Limit to top 10
                try:
                    proc_info = proc.as_dict(['pid', 'name', 'cpu_percent', 'memory_percent'])
                    if proc_info['cpu_percent'] > 0:
                        top_cpu.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cpu_percent': proc_info['cpu_percent']
                        })
                    if proc_info['memory_percent'] > 0:
                        top_mem.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'memory_percent': proc_info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            metrics['top_cpu'] = sorted(top_cpu, key=lambda x: x['cpu_percent'], reverse=True)[:5]
            metrics['top_memory'] = sorted(top_mem, key=lambda x: x['memory_percent'], reverse=True)[:5]

            return metrics
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
            return {
                'count': None,
                'threads': None
            }

    def collect_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = int(time.time() - psutil.boot_time())

            metrics = {
                'uptime': uptime,
                'boot_time': boot_time.isoformat()
            }

            # Add platform information
            import platform
            metrics['platform'] = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }

            return metrics
        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
            return {
                'uptime': None,
                'boot_time': None
            }

    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all system metrics"""
        current_time = time.time()

        metrics = {
            'cpu': self.collect_cpu_metrics(),
            'memory': self.collect_memory_metrics(),
            'disk': self.collect_disk_metrics(),
            'network': self.collect_network_metrics(),
            'processes': self.collect_process_metrics(),
            'system': self.collect_system_info(),
            'collected_at': datetime.utcnow().isoformat()
        }

        self.last_collection_time = current_time

        logger.info("Successfully collected system metrics")
        return metrics

    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature if available"""
        try:
            # Try to get temperature sensors
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Look for CPU temperature
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            if entries:
                                return entries[0].current
                    # If no CPU specific, return first available
                    for entries in temps.values():
                        if entries:
                            return entries[0].current
        except Exception as e:
            logger.debug(f"Could not get CPU temperature: {e}")

        return None


def format_metrics_for_display(metrics: Dict[str, Any]) -> str:
    """Format metrics for human-readable display"""
    lines = []
    lines.append("=" * 50)
    lines.append("SYSTEM METRICS")
    lines.append("=" * 50)

    # CPU
    cpu = metrics.get('cpu', {})
    lines.append(f"CPU Usage: {cpu.get('usage_percent', 0):.1f}%")
    lines.append(f"CPU Cores: {cpu.get('cores', 'N/A')}")
    if cpu.get('load_average'):
        load = cpu['load_average']
        lines.append(f"Load Average: {load.get('1m', 0):.2f}, {load.get('5m', 0):.2f}, {load.get('15m', 0):.2f}")

    # Memory
    mem = metrics.get('memory', {})
    lines.append(f"\nMemory Usage: {mem.get('percent', 0):.1f}%")
    lines.append(f"Memory: {mem.get('used', 0):,} MB / {mem.get('total', 0):,} MB")

    # Disk
    disk = metrics.get('disk', {})
    lines.append(f"\nDisk Usage: {disk.get('percent', 0):.1f}%")
    lines.append(f"Disk: {disk.get('used', 0):.1f} GB / {disk.get('total', 0):.1f} GB")

    # Network
    net = metrics.get('network', {})
    if net.get('bytes_sent') is not None:
        lines.append(f"\nNetwork Sent: {net['bytes_sent'] / (1024*1024*1024):.2f} GB")
        lines.append(f"Network Recv: {net['bytes_recv'] / (1024*1024*1024):.2f} GB")

    # Processes
    proc = metrics.get('processes', {})
    if proc.get('count') is not None:
        lines.append(f"\nProcesses: {proc['count']}")
        lines.append(f"Threads: {proc.get('threads', 'N/A')}")

    # System
    sys = metrics.get('system', {})
    if sys.get('uptime') is not None:
        uptime_days = sys['uptime'] // 86400
        uptime_hours = (sys['uptime'] % 86400) // 3600
        lines.append(f"\nUptime: {uptime_days} days, {uptime_hours} hours")

    lines.append("=" * 50)

    return "\n".join(lines)


if __name__ == "__main__":
    # Test the metrics collector
    collector = MetricsCollector()
    metrics = collector.collect_all_metrics()
    print(format_metrics_for_display(metrics))
    print("\nJSON Output:")
    print(json.dumps(metrics, indent=2, default=str))
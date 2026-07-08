import platform
import psutil
from datetime import datetime
class HardwareInfo:
    def __init__(self):
        self._cache = {}
        self._cache_time = None
        self._cache_duration = 300  # 5 minutes
    def get_cpu_info(self):
        try:
            cpu_info = {
                'model': platform.processor() or "Unknown",
                'physical_cores': psutil.cpu_count(logical=False) or 0,
                'logical_cores': psutil.cpu_count(logical=True) or 0,
                'max_frequency': 0,
                'min_frequency': 0,
                'current_frequency': 0
            }
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info['max_frequency'] = round(cpu_freq.max, 2)
                cpu_info['min_frequency'] = round(cpu_freq.min, 2)
                cpu_info['current_frequency'] = round(cpu_freq.current, 2)

            return cpu_info
        except Exception:
            return {
                'model': 'Unknown',
                'physical_cores': 0,
                'logical_cores': 0,
                'max_frequency': 0,
                'min_frequency': 0,
                'current_frequency': 0
            }
    def get_memory_info(self):
        """Get RAM information"""
        try:
            mem = psutil.virtual_memory()
            return {
                'total_gb': round(mem.total / (1024**3), 2),
                'available_gb': round(mem.available / (1024**3), 2),
                'used_gb': round(mem.used / (1024**3), 2),
                'percentage': mem.percent,
                'total_bytes': mem.total
            }
        except Exception:
            return {
                'total_gb': 0,
                'available_gb': 0,
                'used_gb': 0,
                'percentage': 0,
                'total_bytes': 0
            }
    def get_disk_info(self):
        """Get disk information"""
        try:
            disk_info = {
                'partitions': [],
                'total_partitions': 0
            }
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info['partitions'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'percentage': usage.percent
                    })
                except PermissionError:
                    continue
            disk_info['total_partitions'] = len(disk_info['partitions'])
            return disk_info
        except Exception:
            return {'partitions': [], 'total_partitions': 0}
    def get_network_info(self):
        """Get network adapter information"""
        try:
            network_info = {
                'adapters': [],
                'total_adapters': 0
            }
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            for interface, addresses in net_if_addrs.items():
                adapter = {
                    'name': interface,
                    'addresses': [],
                    'status': 'Unknown',
                    'speed': 0
                }
                if interface in net_if_stats:
                    stats = net_if_stats[interface]
                    adapter['status'] = 'Up' if stats.isup else 'Down'
                    adapter['speed'] = stats.speed
                for addr in addresses:
                    if addr.family.name == 'AF_INET':
                        adapter['addresses'].append(addr.address)
                network_info['adapters'].append(adapter)
            network_info['total_adapters'] = len(network_info['adapters'])
            return network_info
        except Exception:
            return {'adapters': [], 'total_adapters': 0}
    def get_system_info(self):
        """Get operating system information"""
        try:
            return {
                'os_name': platform.system(),
                'os_version': platform.version(),
                'os_release': platform.release(),
                'architecture': platform.machine(),
                'hostname': platform.node(),
                'python_version': platform.python_version()
            }
        except Exception:
            return {
                'os_name': 'Unknown',
                'os_version': 'Unknown',
                'os_release': 'Unknown',
                'architecture': 'Unknown',
                'hostname': 'Unknown',
                'python_version': 'Unknown'
            }
    def get_battery_info(self):
        """Get battery information (for laptops)"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return None
            info = {
                'percentage': battery.percent,
                'plugged_in': battery.power_plugged,
                'time_remaining': battery.secsleft
            }
            if battery.secsleft > 0:
                hours = battery.secsleft // 3600
                minutes = (battery.secsleft % 3600) // 60
                info['time_remaining_formatted'] = f"{hours}h {minutes}m"
            else:
                info['time_remaining_formatted'] = (
                    "Charging" if battery.power_plugged else "Calculating..."
                )
            return info
        except Exception:
            return None
    def get_boot_time(self):
        """Get system boot time"""
        try:
            boot = psutil.boot_time()
            return {
                'timestamp': boot,
                'formatted': datetime.fromtimestamp(boot).strftime("%Y-%m-%d %H:%M:%S"),
                'uptime_seconds': datetime.now().timestamp() - boot
            }
        except Exception:
            return {
                'timestamp': 0,
                'formatted': 'Unknown',
                'uptime_seconds': 0
            }
    def get_all_hardware_info(self, use_cache=True):
        """Get all hardware information at once"""
        if use_cache and self._cache and self._cache_time:
            if datetime.now().timestamp() - self._cache_time < self._cache_duration:
                return self._cache
        self._cache = {
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'system': self.get_system_info(),
            'battery': self.get_battery_info(),
            'boot': self.get_boot_time(),
            'collected_at': datetime.now().isoformat()
        }
        self._cache_time = datetime.now().timestamp()
        return self._cache
    def get_summary(self):
        """Get a quick summary"""
        try:
            cpu = self.get_cpu_info()
            memory = self.get_memory_info()
            system = self.get_system_info()
            disk = self.get_disk_info()
            return {
                'cpu_model': cpu['model'],
                'cpu_cores': f"{cpu['physical_cores']} cores",
                'ram_total': f"{memory['total_gb']} GB",
                'os_name': f"{system['os_name']} {system['os_release']}",
                'hostname': system['hostname'],
                'total_disks': disk['total_partitions']
            }
        except Exception:
            return {}
    def clear_cache(self):
        """Clear cached data"""
        self._cache = {}
        self._cache_time = None
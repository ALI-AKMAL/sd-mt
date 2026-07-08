import time
import psutil
GB = 1024 ** 3
MB_BITS = 8 / (1024 * 1024)
class SystemMonitor:
    def __init__(self):
        net = psutil.net_io_counters()
        self.last_net_io = net
        self.last_net_time = time.time()
        self.start_bytes_sent = net.bytes_sent
        self.start_bytes_recv = net.bytes_recv
        psutil.cpu_percent(interval=0.1)  # Prime CPU measurement
        print(f"✓ Network monitoring initialized")
        print(f"  Initial download: {net.bytes_recv / GB:.3f} GB")
        print(f"  Initial upload:   {net.bytes_sent / GB:.3f} GB")

    def get_usage(self):
        try:
            cpu = psutil.cpu_percent(interval=0)
            mem = psutil.virtual_memory().percent
            for path in ('/', 'C:\\'):
                try:
                    disk = psutil.disk_usage(path).percent
                    break
                except OSError:
                    disk = 0.0
            return cpu, mem, disk
        except Exception as e:
            print(f"Error in get_usage: {e}")
            return 0.0, 0.0, 0.0

    def get_network_usage(self):
        """
        Returns: (download_mbps, upload_mbps, total_sent_gb, total_recv_gb)
        """
        try:
            current = psutil.net_io_counters()
            now = time.time()
            dt = max(now - self.last_net_time, 0.01)

            sent_diff = max(0, current.bytes_sent - self.last_net_io.bytes_sent)
            recv_diff = max(0, current.bytes_recv - self.last_net_io.bytes_recv)

            upload_mbps   = max(0, sent_diff / dt * MB_BITS)
            download_mbps = max(0, recv_diff / dt * MB_BITS)
            total_sent_gb = max(0, (current.bytes_sent - self.start_bytes_sent) / GB)
            total_recv_gb = max(0, (current.bytes_recv - self.start_bytes_recv) / GB)

            self.last_net_io = current
            self.last_net_time = now

            return download_mbps, upload_mbps, total_sent_gb, total_recv_gb
        except Exception as e:
            print(f"Network error: {e}")
            return 0.0, 0.0, 0.0, 0.0

    def get_disk_info(self):
        partitions = []
        for p in psutil.disk_partitions():
            try:
                u = psutil.disk_usage(p.mountpoint)
                partitions.append({
                    'device':     p.device,
                    'mountpoint': p.mountpoint,
                    'filesystem': p.fstype,
                    'total_gb':   round(u.total / GB, 2),
                    'used_gb':    round(u.used  / GB, 2),
                    'free_gb':    round(u.free  / GB, 2),
                    'percent':    u.percent
                })
            except (PermissionError, OSError):
                continue
        return {'partitions': partitions, 'total_disks': len(partitions)}

    def get_detailed_info(self):
        try:
            freq = psutil.cpu_freq()
            mem  = psutil.virtual_memory()
            return {
                'cpu': {
                    'percent':        psutil.cpu_percent(interval=0.1),
                    'physical_cores': psutil.cpu_count(logical=False),
                    'logical_cores':  psutil.cpu_count(logical=True),
                    'frequency_current': freq.current if freq else 0
                },
                'memory': {
                    'percent':      mem.percent,
                    'total_gb':     mem.total     / GB,
                    'available_gb': mem.available / GB,
                    'used_gb':      mem.used      / GB
                },
                'disk': self.get_disk_info()
            }
        except Exception as e:
            print(f"Detailed info error: {e}")
            return {}
_NET_STATUS = [(50, "HEAVY"), (10, "ACTIVE"), (1, "LIGHT"), (0, "IDLE")]
def _net_status(total_mbps):
    return next(label for threshold, label in _NET_STATUS if total_mbps > threshold)
def main():
    print("=" * 70)
    print("System Monitor Backend - Network Test")
    print("=" * 70)
    monitor = SystemMonitor()
    for i in range(1, 21):
        cpu, mem, disk = monitor.get_usage()
        down, up, total_down, total_up = monitor.get_network_usage()
        print(f"[{i:2d}/20] CPU: {cpu:5.1f}% | RAM: {mem:5.1f}% | Disk: {disk:5.1f}%")
        print(f"        Network: ↓ {down:6.2f} Mbps | ↑ {up:6.2f} Mbps [{_net_status(down + up)}]")
        print(f"        Total:   ↓ {total_down:6.3f} GB   | ↑ {total_up:6.3f} GB\n")
        time.sleep(0.5)
    print("=" * 70)
if __name__ == "__main__":
    main()
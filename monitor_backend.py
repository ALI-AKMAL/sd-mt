import time
import psutil
GB = 1024 ** 3
MB_BITS = 8 / (1024 * 1024)  # bytes/sec -> megabits/sec

class SystemMonitor:
    def __init__(self):
        # cpu_percent needs a previous reading to compare against,
        # so this first call just sets that baseline (return value unused)
        psutil.cpu_percent(interval=0)
        net = psutil.net_io_counters()
        self.last_net_io = net
        self.last_net_time = time.time()
        self.start_bytes_sent = net.bytes_sent
        self.start_bytes_recv = net.bytes_recv

    def get_usage(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            disk = 0.0
            for path in ('/', 'C:\\'):
                try:
                    disk = psutil.disk_usage(path).percent
                    break
                except OSError:
                    continue

            return cpu, mem, disk
        except Exception as e:
            print(f"Error in get_usage: {e}")
            return 0.0, 0.0, 0.0

    def get_network_usage(self):
        try:
            current = psutil.net_io_counters()
            now = time.time()
            dt = max(now - self.last_net_time, 0.01)  # avoid divide-by-zero

            sent_diff = max(0, current.bytes_sent - self.last_net_io.bytes_sent)
            recv_diff = max(0, current.bytes_recv - self.last_net_io.bytes_recv)

            upload_mbps = sent_diff / dt * MB_BITS
            download_mbps = recv_diff / dt * MB_BITS
            total_sent_gb = (current.bytes_sent - self.start_bytes_sent) / GB
            total_recv_gb = (current.bytes_recv - self.start_bytes_recv) / GB

            self.last_net_io = current
            self.last_net_time = now

            return download_mbps, upload_mbps, total_sent_gb, total_recv_gb
        except Exception as e:
            print(f"Network error: {e}")
            return 0.0, 0.0, 0.0, 0.0

if __name__ == "__main__":
    monitor = SystemMonitor()
    for i in range(20):
        cpu, mem, disk = monitor.get_usage()
        down, up, total_down, total_up = monitor.get_network_usage()
        print(f"CPU: {cpu:.1f}% | RAM: {mem:.1f}% | Disk: {disk:.1f}% | "
              f"Down: {down:.2f} Mbps | Up: {up:.2f} Mbps")
        time.sleep(0.5)
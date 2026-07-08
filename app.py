import tkinter as tk
from tkinter import ttk
import time
from collections import deque
import threading
try:
    from .cleanup_tab import CleanupTabMixin
    from .hardware_tab import HardwareTabMixin
    from .monitoring_tab import MonitoringTabMixin
    from .process_tab import ProcessTabMixin
    from .settings_tab import SettingsTabMixin
    from .keyboard_tab import KeyboardTabMixin
except ImportError:
    # Fallback when running app.py directly
    from cleanup_tab import CleanupTabMixin
    from hardware_tab import HardwareTabMixin
    from monitoring_tab import MonitoringTabMixin
    from process_tab import ProcessTabMixin
    from settings_tab import SettingsTabMixin
    from keyboard_tab import KeyboardTabMixin
class SystemMonitorUI(
    SettingsTabMixin,
    ProcessTabMixin,
    CleanupTabMixin,
    HardwareTabMixin,
    MonitoringTabMixin,
    KeyboardTabMixin
):
    """
    Complete UI with real-time graphs and hardware information
    """
    # Color scheme
    COLORS = {
    # Main surfaces (soft dark, not pure black)
    'bg_dark': '#202020',        # main app background (Win11 dark)
    'bg_medium': '#2B2B2B',      # sidebar / navigation
    'bg_light': '#313131',       # cards / panels

    # Accent (Windows 11 signature soft blue)
    'accent': '#4CC2FF',         # primary interactive color

    # Text system (soft white, not harsh pure white)
    'text': '#FFFFFF',
    'text_dim': '#A0A0A0',

    # System metrics (clean + consistent)
    'cpu_color': '#4CAF50',      # green (CPU OK)
    'mem_color': '#FFB74D',      # soft orange (RAM)
    'disk_color': '#64B5F6',     # soft blue (disk)

    # Network (balanced, not neon)
    'net_down_color': '#4CC2FF', # download (accent blue)
    'net_up_color': '#EF5350',   # upload (soft red)

    # Status colors (Win11-like system feedback)
    'success': '#4CAF50',
    'warning': '#FFB74D',
    'danger': '#EF5350',

    # Graph / dashboard styling
    'graph_bg': '#1B1B1B',       # slightly darker than main bg
    'grid_color': '#3A3A3A'      # subtle grid lines
}
    # Light theme colors 
    COLORS_LIGHT = {
        'bg_dark': '#f5f5f5',
        'bg_medium': '#ffffff',
        'bg_light': '#e8e8e8',
        'accent': '#0066cc',
        'text': '#1a1a1a',
        'text_dim': '#666666',
        'cpu_color': '#00aa66',
        'mem_color': '#cc0000',
        'disk_color': '#ff9900',
        'net_down_color': '#0066cc',
        'net_up_color': '#cc0000',
        'success': '#00aa66',
        'warning': '#ff9900',
        'danger': '#cc0000',
        'graph_bg': '#fafafa',
        'grid_color': '#dddddd'
    }
    ALERT_COOLDOWN_SECONDS = 20
    def __init__(self, root, monitor_backend, hardware_backend, cleanup_backend, process_backend, current_user=None, db_manager=None):
        """Initialize the UI"""
        self.root = root
        self.monitor = monitor_backend
        self.hardware = hardware_backend
        self.cleanup = cleanup_backend
        self.process_manager = process_backend
        self.current_user = current_user
        self.db_manager = db_manager
        self.running = True
        self._monitor_update_pending = False
        self._alert_state = {}
        self._toast_widgets = []
        # Theme and settings
        self.current_theme = 'dark'  # default theme
        self.update_interval = 500  # milliseconds
        self.auto_start_monitoring = True
        self.show_notifications = True
        # Data storage for graphs (keep last 60 data points = 30 seconds)
        self.max_data_points = 60
        self.cpu_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        self.mem_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        self.disk_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        self.net_down_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        self.net_up_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
        self.load_user_settings()

        # Setup window
        self.setup_window()
        # Create UI
        self.create_ui()
        # Start monitoring
        if self.auto_start_monitoring:
            self.start_monitoring()
        else:
            self.status_label.config(text='Monitoring Paused (Auto-start disabled)', fg=self.COLORS['warning'])

    def show_toast(self, message, error=True, duration_ms=4000):
        """Show a floating pop-up banner in the corner of the window.

        Unlike show_notification (which just changes the footer label text),
        this creates an actual Toplevel widget that overlays the app, so it's
        impossible to miss even if you're not watching the footer.
        """
        try:
            toast = tk.Toplevel(self.root)
            toast.overrideredirect(True)   # no title bar/border
            toast.attributes('-topmost', True)
            try:
                toast.attributes('-alpha', 0.96)
            except tk.TclError:
                pass  # -alpha isn't supported on every platform

            bg_color = self.COLORS['danger'] if error else self.COLORS['success']

            frame = tk.Frame(toast, bg=bg_color, padx=16, pady=12)
            frame.pack(fill='both', expand=True)

            tk.Label(
                frame,
                text=message,
                font=('Segoe UI', 11, 'bold'),
                bg=bg_color,
                fg='#FFFFFF',
                wraplength=340,
                justify='left'
            ).pack(side='left')

            close_btn = tk.Button(
                frame,
                text='✕',
                font=('Segoe UI', 9, 'bold'),
                bg=bg_color,
                fg='#FFFFFF',
                bd=0,
                activebackground=bg_color,
                cursor='hand2',
                command=toast.destroy
            )
            close_btn.pack(side='right', padx=(10, 0))

            # Position: stack toasts in the bottom-right corner of the main window
            self.root.update_idletasks()
            root_x = self.root.winfo_x()
            root_y = self.root.winfo_y()
            root_w = self.root.winfo_width()
            root_h = self.root.winfo_height()

            toast.update_idletasks()
            toast_w = max(toast.winfo_reqwidth(), 260)
            toast_h = toast.winfo_reqheight()

            # Clean up any toasts that were already destroyed (e.g. via the X button)
            self._toast_widgets = [t for t in self._toast_widgets if t.winfo_exists()]
            stack_offset = len(self._toast_widgets) * (toast_h + 10)

            x = root_x + root_w - toast_w - 20
            y = root_y + root_h - toast_h - 60 - stack_offset

            toast.geometry(f"{toast_w}x{toast_h}+{x}+{y}")

            self._toast_widgets.append(toast)

            def _remove():
                if toast in self._toast_widgets:
                    self._toast_widgets.remove(toast)
                if toast.winfo_exists():
                    toast.destroy()

            toast.after(duration_ms, _remove)
        except Exception as e:
            print(f"Could not show toast: {e}")

    def _dispatch_alert(self, key, message, is_error, active):
        """Send alert/recovery notifications with cooldown to avoid spam."""
        if not self.show_notifications:
            return

        now = time.time()
        state = self._alert_state.get(key, {'active': False, 'last_sent': 0.0})

        if active:
            should_send = (not state['active']) or (now - state['last_sent'] >= self.ALERT_COOLDOWN_SECONDS)
            if should_send:
                if hasattr(self, 'show_notification'):
                    self.show_notification(message, error=is_error)
                self.show_toast(message, error=is_error , duration_ms=6000)
                state['last_sent'] = now
            state['active'] = True
        else:
            if state['active']:
                if hasattr(self, 'show_notification'):
                    self.show_notification(f"{message} resolved", error=False)
                self.show_toast(f"{message} resolved", error=False , duration_ms=6000)
                state['last_sent'] = now
            state['active'] = False

        self._alert_state[key] = state

    def check_alerts(self, cpu, mem, disk, down_mbps, up_mbps):
        """Evaluate live metrics and trigger alerts."""
        total_net = down_mbps + up_mbps

        # CPU alerts
        self._dispatch_alert('cpu_high', f"ALERT: CPU high ({cpu:.1f}%)", True, cpu >= 20.0)
        self._dispatch_alert('cpu_critical', f"CRITICAL: CPU very high ({cpu:.1f}%)", True, cpu >= 95.0)

        # Memory alerts
        self._dispatch_alert('mem_high', f"ALERT: Memory high ({mem:.1f}%)", True, mem >= 85.0)
        self._dispatch_alert('mem_critical', f"CRITICAL: Memory very high ({mem:.1f}%)", True, mem >= 95.0)

        # Disk alerts
        self._dispatch_alert('disk_high', f"ALERT: Disk usage high ({disk:.1f}%)", True, disk >= 90.0)
        self._dispatch_alert('disk_critical', f"CRITICAL: Disk almost full ({disk:.1f}%)", True, disk >= 97.0)

        # Network alerts
        self._dispatch_alert('net_active', f"INFO: Network active ({total_net:.1f} Mbps)", False, total_net >= 50.0)
        self._dispatch_alert('net_heavy', f"ALERT: Network heavy ({total_net:.1f} Mbps)", True, total_net >= 100.0)

        # Combined pressure alert
        self._dispatch_alert(
            'system_pressure',
            f"CRITICAL: System pressure high (CPU {cpu:.1f}% / RAM {mem:.1f}%)",
            True,
            cpu >= 90.0 and mem >= 90.0,
        )

    def load_user_settings(self):
        """Load persisted user settings and apply defaults."""
        try:
            if not self.db_manager or not self.current_user:
                return
            user_id = self.current_user.get('user_id') if isinstance(self.current_user, dict) else None
            if not user_id:
                return

            settings = self.db_manager.get_user_settings(user_id)
            self.current_theme = settings.get('theme', 'dark')
            self.update_interval = int(settings.get('update_interval', 500))
            self.auto_start_monitoring = bool(settings.get('auto_start_monitoring', True))
            self.show_notifications = bool(settings.get('show_notifications', True))

            if self.current_theme == 'light':
                self.COLORS = self.COLORS_LIGHT.copy()
        except Exception as e:
            print(f'Could not load user settings: {e}')

    def setup_window(self):
        """Configure main window"""
        self.root.title("System Monitor - Live Graphs Edition")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        self.root.configure(bg=self.COLORS['bg_dark'])
        # Center window
        self.center_window()
        # Handle window close 
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_ui(self):
        """Create the user interface"""
        # Header
        self.create_header()
        # Notebook (tabs)
        self.create_notebook()
        # Footer
        self.create_footer()

    def create_header(self):
        """Create header section"""
        header = tk.Frame(self.root, bg=self.COLORS['bg_dark'], height=70)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        # Title
        title_label = tk.Label(
            header,
            text="⚡ System Monitor",
            font=('Segoe UI', 22, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['accent']
        )
        title_label.pack(pady=15)

    def create_notebook(self):
        """Create tabbed interface"""
        # Container
        notebook_container = tk.Frame(self.root, bg=self.COLORS['bg_dark'])
        notebook_container.pack(fill='both', expand=True, padx=20, pady=10)
        # Create notebook
        style = ttk.Style()
        style.theme_use('default')
        # Configure notebook to expand tabs
        style.configure(
            'Custom.TNotebook',
            background=self.COLORS['bg_dark'],
            borderwidth=0,
            tabmargins=[0, 0, 0, 0]
        )
        # Make tabs stretch to fill width equally
        style.configure(
            'Custom.TNotebook.Tab',
            background=self.COLORS['bg_medium'],
            foreground=self.COLORS['text_dim'],
            padding=[20, 10],
            font=('Segoe UI', 10, 'bold'),
            expand=[1, 1, 1]  # Expand tabs to fill space
        )
        style.map(
            'Custom.TNotebook.Tab',
            background=[('selected', self.COLORS['bg_light'])],
            foreground=[('selected', self.COLORS['accent'])],
            expand=[('selected', [1, 1, 1])]
        )
        # Layout to make tabs fill entire width
        style.layout('Custom.TNotebook.Tab', [
            ('Notebook.tab', {
                'sticky': 'nswe',
                'children': [
                    ('Notebook.padding', {
                        'side': 'top',
                        'sticky': 'nswe',
                        'children': [
                            ('Notebook.label', {'side': 'top', 'sticky': ''})
                        ]
                    })
                ]
            })
        ])
        
        self.notebook = ttk.Notebook(notebook_container, style='Custom.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        # Create tabs
        self.create_monitoring_tab()
        self.create_hardware_tab()
        self.create_cleanup_tab()
        self.create_process_tab()
        self.create_keyboard_tab()
        self.create_settings_tab()
        
        # Force tabs to stretch by binding to configure event
        def on_tab_configure(event):
            # Calculate width per tab (divide available width by number of tabs)
            num_tabs = self.notebook.index('end')
            if num_tabs > 0:
                tab_width = event.width // num_tabs
                style.configure('Custom.TNotebook.Tab', width=tab_width)
        self.notebook.bind('<Configure>', on_tab_configure)

    def create_footer(self):
        """Create footer section"""
        footer = tk.Frame(self.root, bg=self.COLORS['bg_medium'], height=45)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        self.status_label = tk.Label(
            footer,
            text="● Monitoring Active",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['success']
        )
        self.status_label.pack(side='left', padx=25, pady=12)
        self.update_label = tk.Label(
            footer,
            text="Last update: --:--:--",
            font=('Segoe UI', 8),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        )
        self.update_label.pack(side='right', padx=25, pady=12)

    def start_monitoring(self):
        """Start monitoring in background"""
        def _next_sleep():
            # Keep UI smooth by capping redraw pressure even if user picks very low intervals.
            return max(0.35, self.update_interval / 1000.0)

        def monitor_loop():
            while self.running:
                try:
                    cpu, mem, disk = self.monitor.get_usage()
                    down_mbps, up_mbps, total_down_gb, total_up_gb = self.monitor.get_network_usage()
                    # Add to data queues
                    self.cpu_data.append(cpu)
                    self.mem_data.append(mem)
                    self.disk_data.append(disk)
                    self.net_down_data.append(down_mbps)
                    self.net_up_data.append(up_mbps)
                    # Keep only one queued UI update to avoid Tk event backlog under load.
                    if not self._monitor_update_pending:
                        self._monitor_update_pending = True
                        self.root.after(
                            0,
                            self.update_monitoring,
                            cpu,
                            mem,
                            disk,
                            down_mbps,
                            up_mbps,
                            total_down_gb,
                            total_up_gb,
                        )
                    time.sleep(_next_sleep())
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(_next_sleep())
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()

    def update_monitoring(self, cpu, mem, disk, down_mbps, up_mbps, total_down_gb, total_up_gb):
        """Update monitoring display with graphs"""
        self._monitor_update_pending = False
        self.check_alerts(cpu, mem, disk, down_mbps, up_mbps)
        # Update CPU
        self.cpu_percent_label.config(text=f"{cpu:.1f}%")
        self.draw_graph(self.cpu_canvas, self.cpu_data, self.COLORS['cpu_color'])
        if cpu < 50:
            self.cpu_status_label.config(text="Status: Normal", fg=self.COLORS['success'])
            self.cpu_percent_label.config(fg=self.COLORS['success'])
        elif cpu < 80:
            self.cpu_status_label.config(text="Status: High", fg=self.COLORS['warning'])
            self.cpu_percent_label.config(fg=self.COLORS['warning'])
        else:
            self.cpu_status_label.config(text="Status: Critical!", fg=self.COLORS['danger'])
            self.cpu_percent_label.config(fg=self.COLORS['danger'])
        # Update Memory
        self.mem_percent_label.config(text=f"{mem:.1f}%")
        self.draw_graph(self.mem_canvas, self.mem_data, self.COLORS['mem_color'])
        if mem < 50:
            self.mem_status_label.config(text="Status: Normal", fg=self.COLORS['success'])
            self.mem_percent_label.config(fg=self.COLORS['success'])
        elif mem < 80:
            self.mem_status_label.config(text="Status: High", fg=self.COLORS['warning'])
            self.mem_percent_label.config(fg=self.COLORS['warning'])
        else:
            self.mem_status_label.config(text="Status: Critical!", fg=self.COLORS['danger'])
            self.mem_percent_label.config(fg=self.COLORS['danger'])
        # Update Disk
        self.disk_percent_label.config(text=f"{disk:.1f}%")
        self.draw_graph(self.disk_canvas, self.disk_data, self.COLORS['disk_color'])
        if disk < 70:
            self.disk_status_label.config(text="Status: Normal", fg=self.COLORS['success'])
            self.disk_percent_label.config(fg=self.COLORS['success'])
        elif disk < 90:
            self.disk_status_label.config(text="Status: High", fg=self.COLORS['warning'])
            self.disk_percent_label.config(fg=self.COLORS['warning'])
        else:
            self.disk_status_label.config(text="Status: Critical!", fg=self.COLORS['danger'])
            self.disk_percent_label.config(fg=self.COLORS['danger'])
        # Update Network
        self.net_down_label.config(text=f"↓ {down_mbps:.2f} Mbps")
        self.net_up_label.config(text=f"↑ {up_mbps:.2f} Mbps")
        self.draw_network_graph(self.net_canvas, self.net_down_data, self.net_up_data)
        # Network status
        total_speed = down_mbps + up_mbps
        if total_speed < 1:
            self.net_status_label.config(text="Status: Idle", fg=self.COLORS['text_dim'])
        elif total_speed < 10:
            self.net_status_label.config(text="Status: Light Activity", fg=self.COLORS['success'])
        elif total_speed < 50:
            self.net_status_label.config(text="Status: Active", fg=self.COLORS['warning'])
        else:
            self.net_status_label.config(text="Status: Heavy Usage", fg=self.COLORS['danger'])
        # Update total data
        self.net_total_label.config(text=f"Total: ↓ {total_down_gb:.2f} GB | ↑ {total_up_gb:.2f} GB")
        # Update time
        self.update_label.config(text=f"Last update: {time.strftime('%H:%M:%S')}")

    def on_closing(self):
        """Handle window close"""
        self.running = False
        # Unbind scroll events to prevent memory leaks
        try:
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")
        except:
            pass
        self.root.destroy()
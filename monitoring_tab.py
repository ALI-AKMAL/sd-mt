import tkinter as tk
from tkinter import ttk

class MonitoringTabMixin:
    def create_monitoring_tab(self):

        """Create real-time monitoring tab with graphs"""
        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='Live Monitoring')
        # Scrollable frame
        canvas = tk.Canvas(tab, bg=self.COLORS['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['bg_dark'])
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel and trackpad scrolling
        # Enable mouse wheel and trackpad scrolling (Windows)
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            # Bind scroll only when cursor is inside canvas
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Store canvas reference for cleanup
        self.monitoring_canvas = canvas
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Create monitoring sections with graphs
        self.create_cpu_graph(scrollable_frame)
        self.create_memory_graph(scrollable_frame)
        self.create_disk_graph(scrollable_frame)
        self.create_network_graph(scrollable_frame)

    def create_cpu_graph(self, parent):
        """Create CPU monitoring section with graph"""
        # Container
        container = tk.Frame(parent, bg=self.COLORS['bg_dark'])
        container.pack(anchor="w" , padx=130 , pady=30)
        
        cpu_frame = tk.Frame(container, bg=self.COLORS['bg_medium'])
        cpu_frame.pack(fill='x')
        
        # Border
        tk.Frame(cpu_frame, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        # Content
        content = tk.Frame(cpu_frame, bg=self.COLORS['bg_medium'])
        content.pack(fill='both', padx=25, pady=20)
        
        # Header
        header = tk.Frame(content, bg=self.COLORS['bg_medium'])
        header.pack(fill='x')
        
        tk.Label(header, text="🖥️", font=('Segoe UI', 24), bg=self.COLORS['bg_medium']).pack(side='left', padx=(0, 12))
        
        labels = tk.Frame(header, bg=self.COLORS['bg_medium'])
        labels.pack(side='left', fill='x', expand=True)
        
        tk.Label(labels, text="CPU Usage", font=('Segoe UI', 13, 'bold'), bg=self.COLORS['bg_medium'], fg=self.COLORS['text'], anchor='w').pack(fill='x')
        tk.Label(labels, text="Processor activity", font=('Segoe UI', 8), bg=self.COLORS['bg_medium'], fg=self.COLORS['text_dim'], anchor='w').pack(fill='x')
        
        self.cpu_percent_label = tk.Label(header, text="0.0%", font=('Segoe UI', 28, 'bold'), bg=self.COLORS['bg_medium'], fg=self.COLORS['cpu_color'])
        self.cpu_percent_label.pack(side='right')
        
        # Graph canvas
        graph_frame = tk.Frame(content, bg=self.COLORS['graph_bg'], relief='flat', bd=1)
        graph_frame.pack(fill='x', pady=(15, 0))
        
        self.cpu_canvas = tk.Canvas(
            graph_frame,
            width=850,
            height=120,
            bg=self.COLORS['graph_bg'],
            highlightthickness=0
        )
        self.cpu_canvas.pack(padx=5, pady=5)
        
        # Status
        self.cpu_status_label = tk.Label(content, text="Status: Normal", font=('Segoe UI', 8), bg=self.COLORS['bg_medium'], fg=self.COLORS['text_dim'], anchor='w')
        self.cpu_status_label.pack(fill='x', pady=(8, 0))

    def create_memory_graph(self, parent):
        """Create memory monitoring section with graph"""
        container = tk.Frame(parent, bg=self.COLORS['bg_dark'])
        container.pack(anchor="w" , padx=130 , pady=30)
        
        mem_frame = tk.Frame(container, bg=self.COLORS['bg_medium'])
        mem_frame.pack(fill='x')
        
        tk.Frame(mem_frame, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        content = tk.Frame(mem_frame, bg=self.COLORS['bg_medium'])
        content.pack(fill='both', padx=25, pady=20)
        
        header = tk.Frame(content, bg=self.COLORS['bg_medium'])
        header.pack(fill='x')
        
        tk.Label(header, text="💾", font=('Segoe UI', 24), bg=self.COLORS['bg_medium']).pack(side='left', padx=(0, 12))
        
        labels = tk.Frame(header, bg=self.COLORS['bg_medium'])
        labels.pack(side='left', fill='x', expand=True)
        
        tk.Label(labels, text="Memory Usage", font=('Segoe UI', 13, 'bold'), bg=self.COLORS['bg_medium'], fg=self.COLORS['text'], anchor='w').pack(fill='x')
        tk.Label(labels, text="RAM consumption", font=('Segoe UI', 8), bg=self.COLORS['bg_medium'], fg=self.COLORS['text_dim'], anchor='w').pack(fill='x')
        
        self.mem_percent_label = tk.Label(header, text="0.0%", font=('Segoe UI', 28, 'bold'), bg=self.COLORS['bg_medium'], fg=self.COLORS['mem_color'])
        self.mem_percent_label.pack(side='right')
        
        # Graph canvas
        graph_frame = tk.Frame(content, bg=self.COLORS['graph_bg'], relief='flat', bd=1)
        graph_frame.pack(fill='x', pady=(15, 0))
        
        self.mem_canvas = tk.Canvas(
            graph_frame,
            width=850,
            height=120,
            bg=self.COLORS['graph_bg'],
            highlightthickness=0
        )
        self.mem_canvas.pack(padx=5, pady=5)
        
        self.mem_status_label = tk.Label(content, text="Status: Normal", font=('Segoe UI', 8), bg=self.COLORS['bg_medium'], fg=self.COLORS['text_dim'], anchor='w')
        self.mem_status_label.pack(fill='x', pady=(8, 0))

    def create_disk_graph(self, parent):
        """Create disk monitoring section with graph"""
        container = tk.Frame(parent, bg=self.COLORS['bg_dark'])
        container.pack(anchor="w" , padx=130 , pady=30)
        
        disk_frame = tk.Frame(container, bg=self.COLORS['bg_medium'])
        disk_frame.pack(fill='x')
        
        tk.Frame(disk_frame, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        content = tk.Frame(disk_frame, bg=self.COLORS['bg_medium'])
        content.pack(fill='both', padx=25, pady=20)
        
        header = tk.Frame(content, bg=self.COLORS['bg_medium'])
        header.pack(fill='x')
        
        tk.Label(header, text="💿", font=('Segoe UI', 24), bg=self.COLORS['bg_medium']).pack(side='left', padx=(0, 12))
        
        labels = tk.Frame(header, bg=self.COLORS['bg_medium'])
        labels.pack(side='left', fill='x', expand=True)
        
        tk.Label(labels, text="Disk Usage", font=('Segoe UI', 13, 'bold'), bg=self.COLORS['bg_medium'], fg=self.COLORS['text'], anchor='w').pack(fill='x')
        tk.Label(labels, text="Storage consumption", font=('Segoe UI', 8), bg=self.COLORS['bg_medium'], fg=self.COLORS['text_dim'], anchor='w').pack(fill='x')
        
        self.disk_percent_label = tk.Label(header, text="0.0%", font=('Segoe UI', 28, 'bold'), bg=self.COLORS['bg_medium'], fg=self.COLORS['disk_color'])
        self.disk_percent_label.pack(side='right')
        
        # Graph canvas
        graph_frame = tk.Frame(content, bg=self.COLORS['graph_bg'], relief='flat', bd=1)
        graph_frame.pack(fill='x', pady=(15, 0))
        
        self.disk_canvas = tk.Canvas(
            graph_frame,
            width=850,
            height=120,
            bg=self.COLORS['graph_bg'],
            highlightthickness=0
        )
        self.disk_canvas.pack(padx=5, pady=5)
        
        self.disk_status_label = tk.Label(content, text="Status: Normal", font=('Segoe UI', 8), bg=self.COLORS['bg_medium'], fg=self.COLORS['text_dim'], anchor='w')
        self.disk_status_label.pack(fill='x', pady=(8, 0))

    def draw_graph(self, canvas, data, color, max_value=100):
        """Draw a real-time line graph"""
        canvas.delete('all')
        
        width = canvas.winfo_width() if canvas.winfo_width() > 1 else 850
        height = canvas.winfo_height() if canvas.winfo_height() > 1 else 120
        
        # Draw grid lines
        for i in range(0, 101, 25):
            y = height - (i / max_value) * height
            canvas.create_line(0, y, width, y, fill=self.COLORS['grid_color'], dash=(2, 4))
            canvas.create_text(5, y - 5, text=f"{i}%", fill=self.COLORS['text_dim'], anchor='w', font=('Segoe UI', 7))
        
        # Draw graph line
        if len(data) > 1:
            points = []
            num_points = len(data)
            x_step = width / (num_points - 1)
            
            for i, value in enumerate(data):
                x = i * x_step
                y = height - (value / max_value) * height
                points.extend([x, y])
            
            # Draw filled area under line
            if len(points) >= 4:
                fill_points = points.copy()
                fill_points.extend([width, height, 0, height])
                canvas.create_polygon(fill_points, fill=color, stipple='gray25', outline='')
            
            # Draw line
            if len(points) >= 4:
                canvas.create_line(points, fill=color, width=2, smooth=True)
        
        # Draw current value indicator
        if data:
            current = data[-1]
            y = height - (current / max_value) * height
            canvas.create_oval(width - 8, y - 4, width - 2, y + 4, fill=color, outline='')
            canvas.create_text(width - 15, y, text=f"{current:.1f}%", fill=self.COLORS['text'], 
                             anchor='e', font=('Segoe UI', 9, 'bold'))

    def create_network_graph(self, parent):
        """Create network monitoring section with dual graph (download/upload)"""
        # Container
        container = tk.Frame(parent, bg=self.COLORS['bg_dark'])
        container.pack(anchor="w" , padx=130 , pady=30)
        
        net_frame = tk.Frame(container, bg=self.COLORS['bg_medium'])
        net_frame.pack(fill='x')
        
        # Border
        tk.Frame(net_frame, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        # Content
        content = tk.Frame(net_frame, bg=self.COLORS['bg_medium'])
        content.pack(fill='both', padx=25, pady=20)
        
        # Header
        header = tk.Frame(content, bg=self.COLORS['bg_medium'])
        header.pack(fill='x')
        
        tk.Label(header, text="🌐", font=('Segoe UI', 24), bg=self.COLORS['bg_medium']).pack(side='left', padx=(0, 12))
        
        labels = tk.Frame(header, bg=self.COLORS['bg_medium'])
        labels.pack(side='left', fill='x', expand=True)
        
        tk.Label(labels, text="Network Usage", font=('Segoe UI', 13, 'bold'), bg=self.COLORS['bg_medium'], fg=self.COLORS['text'], anchor='w').pack(fill='x')
        tk.Label(labels, text="Download and upload speeds", font=('Segoe UI', 8), bg=self.COLORS['bg_medium'], fg=self.COLORS['text_dim'], anchor='w').pack(fill='x')
        
        # Speed labels
        speed_container = tk.Frame(header, bg=self.COLORS['bg_medium'])
        speed_container.pack(side='right')
        
        self.net_down_label = tk.Label(speed_container, text="↓ 0.00 Mbps", font=('Segoe UI', 12, 'bold'), bg=self.COLORS['bg_medium'], fg=self.COLORS['net_down_color'])
        self.net_down_label.pack(side='top', anchor='e')
        
        self.net_up_label = tk.Label(speed_container, text="↑ 0.00 Mbps", font=('Segoe UI', 12, 'bold'), bg=self.COLORS['bg_medium'], fg=self.COLORS['net_up_color'])
        self.net_up_label.pack(side='top', anchor='e')
        
        # Graph canvas (dual graph for download and upload)
        graph_frame = tk.Frame(content, bg=self.COLORS['graph_bg'], relief='flat', bd=1)
        graph_frame.pack(fill='x', pady=(15, 0))
        
        self.net_canvas = tk.Canvas(
            graph_frame,
            width=850,
            height=150,
            bg=self.COLORS['graph_bg'],
            highlightthickness=0
        )
        self.net_canvas.pack(padx=10, pady=10)
        
        # Status
        self.net_status_label = tk.Label(content, text="Status: Monitoring", font=('Segoe UI', 9), bg=self.COLORS['bg_medium'], fg=self.COLORS['text_dim'])
        self.net_status_label.pack(anchor='w', pady=(8, 0))
        
        # Total data label
        self.net_total_label = tk.Label(content, text="Total: ↓ 0.00 GB | ↑ 0.00 GB", font=('Segoe UI', 9), bg=self.COLORS['bg_medium'], fg=self.COLORS['text_dim'])
        self.net_total_label.pack(anchor='w', pady=(4, 0))

    def draw_network_graph(self, canvas, down_data, up_data):
        """Draw dual network graph (download and upload)"""
        canvas.delete('all')
        
        width = 850
        height = 150
        
        # Find max value for scaling (at least 1 Mbps for visibility)
        max_down = max(down_data) if down_data else 1
        max_up = max(up_data) if up_data else 1
        max_value = max(max_down, max_up, 1)  # Minimum 1 Mbps
        
        # Draw grid lines with labels
        grid_lines = [0, 25, 50, 75, 100]
        for percent in grid_lines:
            y = height - (percent / 100) * height
            canvas.create_line(0, y, width, y, fill=self.COLORS['grid_color'], width=1)
            
            # Scale label based on max value
            label_value = (percent / 100) * max_value
            canvas.create_text(5, y - 5, text=f"{label_value:.1f}", fill=self.COLORS['text_dim'], 
                             anchor='w', font=('Segoe UI', 7))
        
        # Draw download line (cyan)
        if len(down_data) > 1:
            x_step = width / (len(down_data) - 1)
            points = []
            
            for i, value in enumerate(down_data):
                x = i * x_step
                y = height - (value / max_value) * height
                points.extend([x, y])
            
            # Draw filled area
            if len(points) >= 4:
                fill_points = points.copy()
                fill_points.extend([width, height, 0, height])
                canvas.create_polygon(fill_points, fill=self.COLORS['net_down_color'], stipple='gray25', outline='')
            
            # Draw line
            if len(points) >= 4:
                canvas.create_line(points, fill=self.COLORS['net_down_color'], width=2, smooth=True)
            
            # Current value indicator
            current = down_data[-1]
            y = height - (current / max_value) * height
            canvas.create_oval(width - 8, y - 4, width - 2, y + 4, fill=self.COLORS['net_down_color'], outline='')
        
        # Draw upload line (red)
        if len(up_data) > 1:
            x_step = width / (len(up_data) - 1)
            points = []
            
            for i, value in enumerate(up_data):
                x = i * x_step
                y = height - (value / max_value) * height
                points.extend([x, y])
            
            # Draw line (no fill for upload, just line)
            if len(points) >= 4:
                canvas.create_line(points, fill=self.COLORS['net_up_color'], width=2, smooth=True, dash=(4, 2))
            
            # Current value indicator
            current = up_data[-1]
            y = height - (current / max_value) * height
            canvas.create_oval(width - 8, y - 4, width - 2, y + 4, fill=self.COLORS['net_up_color'], outline='')
        
        # Legend
        canvas.create_line(10, 15, 30, 15, fill=self.COLORS['net_down_color'], width=2)
        canvas.create_text(35, 15, text="Download", fill=self.COLORS['text'], anchor='w', font=('Segoe UI', 8))
        
        canvas.create_line(120, 15, 140, 15, fill=self.COLORS['net_up_color'], width=2, dash=(4, 2))
        canvas.create_text(145, 15, text="Upload", fill=self.COLORS['text'], anchor='w', font=('Segoe UI', 8))
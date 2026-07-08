import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

class HardwareTabMixin:
    def create_hardware_tab(self):
        """Create hardware information tab"""
        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='💻 Hardware Info')
        
        # Top controls
        controls = tk.Frame(tab, bg=self.COLORS['bg_dark'])
        controls.pack(fill='x', padx=20, pady=15)
        
        tk.Label(
            controls,
            text="System Hardware Information",
            font=('Segoe UI', 16, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text']
        ).pack(anchor='center')
        
        refresh_btn = tk.Button(
            controls,
            text="🔄 Refresh",
            font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['accent'],
            fg=self.COLORS['bg_dark'],
            activebackground=self.COLORS['bg_light'],
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.refresh_hardware_info
        )
        refresh_btn.pack(side='right')
        
        # Text display
        text_frame = tk.Frame(tab, bg=self.COLORS['bg_medium'])
        text_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.hardware_text = scrolledtext.ScrolledText(
            text_frame,
            font=('Consolas', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            insertbackground=self.COLORS['accent'],
            relief='flat',
            padx=20,
            pady=20,
            wrap='word'
        )
        self.hardware_text.pack(fill='both', expand=True)
        
        # Configure tags
        self.hardware_text.tag_config('header', foreground=self.COLORS['accent'], font=('Consolas', 11, 'bold'), justify='center')
        self.hardware_text.tag_config('label', foreground=self.COLORS['text_dim'] , justify='center')
        self.hardware_text.tag_config('value', foreground=self.COLORS['text'], font=('Consolas', 10, 'bold') , justify='center')
        
        # Load hardware info
        self.load_hardware_info()

    def load_hardware_info(self):
        """Load hardware information"""
        def load_thread():
            try:
                info = self.hardware.get_all_hardware_info()
                self.root.after(0, self.display_hardware_info, info)
            except Exception as e:
                error_msg = f"Error loading hardware info: {e}"
                self.root.after(0, lambda: self.hardware_text.insert('1.0', error_msg))
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    def display_hardware_info(self, info):
        """Display hardware information"""
        self.hardware_text.delete('1.0', tk.END)
        
        def add_line(text, tag='value'):
            self.hardware_text.insert(tk.END, text + '\n', tag)
        
        # CPU
        add_line('═' * 140, 'header')
        add_line('CPU INFORMATION', 'header')
        add_line('═' * 140, 'header')
        cpu = info['cpu']
        add_line(f"Model:            {cpu['model']}")
        add_line(f"Physical Cores:   {cpu['physical_cores']}")
        add_line(f"Logical Cores:    {cpu['logical_cores']}")
        add_line(f"Max Frequency:    {cpu['max_frequency']} MHz")
        add_line(f"Current Freq:     {cpu['current_frequency']} MHz")
        add_line('')
        
        # Memory
        add_line('═' * 140, 'header')
        add_line('MEMORY INFORMATION', 'header')
        add_line('═' * 140, 'header')
        mem = info['memory']
        add_line(f"Total RAM:        {mem['total_gb']} GB")
        add_line(f"Available:        {mem['available_gb']} GB")
        add_line(f"Used:             {mem['used_gb']} GB")
        add_line(f"Usage:            {mem['percentage']}%")
        add_line('')
        
        # Disk
        add_line('═' * 140, 'header')
        add_line('DISK INFORMATION', 'header')
        add_line('═' * 140, 'header')
        disk = info['disk']
        add_line(f"Total Partitions: {disk['total_partitions']}")
        for i, part in enumerate(disk['partitions'], 1):
            add_line(f"\nPartition {i}:")
            add_line(f"  Device:         {part['device']}")
            add_line(f"  Mount:          {part['mountpoint']}")
            add_line(f"  Filesystem:     {part['filesystem']}")
            add_line(f"  Total:          {part['total_gb']} GB")
            add_line(f"  Used:           {part['used_gb']} GB")
            add_line(f"  Free:           {part['free_gb']} GB")
            add_line(f"  Usage:          {part['percentage']}%")
        add_line('')
        
        # System
        add_line('═' * 140, 'header')
        add_line('SYSTEM INFORMATION', 'header')
        add_line('═' * 140, 'header')
        sys = info['system']
        add_line(f"OS:               {sys['os_name']} {sys['os_release']}")
        add_line(f"Version:          {sys['os_version']}")
        add_line(f"Architecture:     {sys['architecture']}")
        add_line(f"Hostname:         {sys['hostname']}")
        add_line('')
        
        # Battery
        add_line('═' * 140, 'header')
        add_line('BATTERY INFORMATION', 'header')
        add_line('═' * 140, 'header')
        battery = info['battery']
        if battery:
            add_line(f"Battery Level:    {battery['percentage']}%")
            add_line(f"Plugged In:       {'Yes' if battery['plugged_in'] else 'No'}")
            add_line(f"Time Remaining:   {battery['time_remaining_formatted']}")
        else:
            add_line("No battery detected (Desktop PC)")
        
        self.hardware_text.config(state='disabled')

    def refresh_hardware_info(self):
        """Refresh hardware information"""
        self.hardware.clear_cache()
        self.hardware_text.config(state='normal')
        self.hardware_text.delete('1.0', tk.END)
        self.hardware_text.insert('1.0', 'Refreshing hardware information...\n')
        self.load_hardware_info()
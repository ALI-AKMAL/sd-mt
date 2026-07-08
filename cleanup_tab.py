import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import threading
class CleanupTabMixin:
    def create_cleanup_tab(self):
        """Create cleanup tab"""
        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='Cleanup')
        # Main container
        main = tk.Frame(tab, bg=self.COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Title
        title_frame = tk.Frame(main, bg=self.COLORS['bg_dark'])
        title_frame.pack(fill='x', pady=(0, 20))
        tk.Label(
            title_frame,
            text="System Cleanup & File Management",
            font=('Segoe UI', 18, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text']
        ).pack(side='left')
        
        # Disk space info
        disk_frame = tk.Frame(main, bg=self.COLORS['bg_medium'], relief='flat')
        disk_frame.pack(fill='x', pady=(0, 20))
        
        tk.Frame(disk_frame, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        disk_content = tk.Frame(disk_frame, bg=self.COLORS['bg_medium'])
        disk_content.pack(fill='x', padx=25, pady=20)
        
        tk.Label(
            disk_content,
            text="Disk Space Overview",
            font=('Segoe UI', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 10))
        
        self.disk_info_label = tk.Label(
            disk_content,
            text="Loading disk information...",
            font=('Segoe UI', 11),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim'],
            justify='left'
        )
        self.disk_info_label.pack(anchor='w')
        
        # Cleanup buttons
        buttons_frame = tk.Frame(main, bg=self.COLORS['bg_dark'])
        buttons_frame.pack(fill='x', pady=(0, 20))
        
        # Scan button
        self.scan_btn = tk.Button(
            buttons_frame,
            text="Scan Temp Files",
            font=('Segoe UI', 12, 'bold'),
            bg=self.COLORS['accent'],
            fg=self.COLORS['bg_dark'],
            activebackground=self.COLORS['bg_light'],
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.scan_temp_files
        )
        self.scan_btn.pack(side='left', padx=(0, 10))
        
        # Open file manager button
        open_files_btn = tk.Button(
            buttons_frame,
            text="Open File Manager",
            font=('Segoe UI', 12, 'bold'),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text'],
            activebackground=self.COLORS['bg_medium'],
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.open_file_manager
        )
        open_files_btn.pack(side='left', padx=(0, 10))
        
        # Open temp folder button
        open_temp_btn = tk.Button(
            buttons_frame,
            text="Open Temp Folder",
            font=('Segoe UI', 12, 'bold'),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text'],
            activebackground=self.COLORS['bg_medium'],
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.open_temp_folder
        )
        open_temp_btn.pack(side='left')
        
        # Results area
        results_frame = tk.Frame(main, bg=self.COLORS['bg_medium'])
        results_frame.pack(fill='both', expand=True)
        
        tk.Frame(results_frame, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        results_content = tk.Frame(results_frame, bg=self.COLORS['bg_medium'])
        results_content.pack(fill='both', expand=True, padx=25, pady=20)
        
        tk.Label(
            results_content,
            text="Scan Results",
            font=('Segoe UI', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 10))
        
        # Results text area
        self.cleanup_text = scrolledtext.ScrolledText(
            results_content,
            font=('Consolas', 10),
            bg=self.COLORS['graph_bg'],
            fg=self.COLORS['text'],
            relief='flat',
            padx=15,
            pady=15,
            wrap='word',
            height=10
        )
        self.cleanup_text.pack(fill='both', expand=True)
        self.cleanup_text.insert('1.0', 'Click "Scan Temp Files" to start scanning...\n')
        self.cleanup_text.config(state='disabled')
        
        # Load disk space
        self.load_disk_space()

    def load_disk_space(self):
        """Load and display disk space information"""
        def load_thread():
            try:
                disk_info = self.cleanup.get_disk_space()
                if disk_info:
                    info_text = (
                        f"Total Space: {disk_info['total_gb']} GB\n"
                        f"Used Space: {disk_info['used_gb']} GB ({disk_info['used_percent']}%)\n"
                        f"Free Space: {disk_info['free_gb']} GB"
                    )
                    self.root.after(0, lambda: self.disk_info_label.config(text=info_text))
            except Exception as e:
                error_text = f"Error loading disk space: {e}"
                self.root.after(0, lambda: self.disk_info_label.config(text=error_text))
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    def scan_temp_files(self):
        """Scan for temporary files"""
        self.scan_btn.config(state='disabled', text='Scanning...')
        self.cleanup_text.config(state='normal')
        self.cleanup_text.delete('1.0', tk.END)
        self.cleanup_text.insert('1.0', 'Scanning temporary files...\nThis may take a moment...\n\n')
        self.cleanup_text.config(state='disabled')
        
        def scan_thread():
            try:
                results = self.cleanup.scan_temp_files()
                self.root.after(0, self.display_scan_results, results)
            except Exception as e:
                error_msg = f"Error during scan: {e}"
                self.root.after(0, self.display_scan_error, error_msg)
        
        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()

    def display_scan_results(self, results):
        """Display scan results"""
        self.cleanup_text.config(state='normal')
        self.cleanup_text.delete('1.0', tk.END)
        
        # Summary
        self.cleanup_text.insert('end', 'SCAN RESULTS\n')
        self.cleanup_text.insert('end', '' * 60 + '\n\n')
        
        self.cleanup_text.insert('end', f"Total Files Found: {results['total_files']:,}\n")
        self.cleanup_text.insert('end', f"Total Size: {results['total_size_mb']:,.2f} MB ")
        self.cleanup_text.insert('end', f"({results['total_size_gb']:.2f} GB)\n\n")
        
        self.cleanup_text.insert('end', '' * 60 + '\n')
        self.cleanup_text.insert('end', 'BY CATEGORY:\n')
        self.cleanup_text.insert('end', '' * 60 + '\n\n')
        
        # Categories
        for category, data in results['categories'].items():
            if data['file_count'] > 0:
                self.cleanup_text.insert('end', f"{category}:\n")
                self.cleanup_text.insert('end', f"Files: {data['file_count']:,}\n")
                self.cleanup_text.insert('end', f"Size: {data['size_mb']:.2f} MB ")
                self.cleanup_text.insert('end', f"({data['size_gb']:.2f} GB)\n\n")
        self.cleanup_text.insert('end', 'â•' * 60 + '\n')
        self.cleanup_text.insert('end', 'NOTE: Use "Open File Manager" to manually delete files\n')
        self.cleanup_text.insert('end', 'â•' * 60 + '\n')
        
        self.cleanup_text.config(state='disabled')
        self.scan_btn.config(state='normal', text='Scan Temp Files')

    def display_scan_error(self, error_msg):
        """Display scan error"""
        self.cleanup_text.config(state='normal')
        self.cleanup_text.delete('1.0', tk.END)
        self.cleanup_text.insert('1.0', f'ERROR: {error_msg}\n')
        self.cleanup_text.config(state='disabled')
        self.scan_btn.config(state='normal', text='Scan Temp Files')

    def open_file_manager(self):
        """Open file manager"""
        success = self.cleanup.open_file_explorer()
        if success:
            self.show_notification("File Manager opened successfully!")
        else:
            self.show_notification("Failed to open File Manager", error=True)

    def open_temp_folder(self):
        """Open temp folder"""
        success = self.cleanup.open_temp_folder()
        if success:
            self.show_notification("Temp folder opened successfully!")
        else:
            self.show_notification("Failed to open Temp folder", error=True)

    def show_notification(self, message, error=False):
        """Show temporary notification"""
        color = self.COLORS['danger'] if error else self.COLORS['success']
        self.status_label.config(text=f" {message}", fg=color)
        
        # Reset after 3 seconds
        def reset():
            self.status_label.config(text="Monitoring Active", fg=self.COLORS['success'])
        self.root.after(3000, reset)
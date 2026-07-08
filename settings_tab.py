import tkinter as tk
from tkinter import ttk
import os
import platform
from collections import deque
class SettingsTabMixin:
    def create_settings_tab(self):
        """Create settings and preferences tab"""
        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='⚙️ Settings')
        
        # Main container with scroll
        canvas = tk.Canvas(tab, bg=self.COLORS['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS['bg_dark'])
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        canvas.bind('<Configure>',
        lambda e: canvas.itemconfig(canvas_window, width=e.width)
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        # canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable scrolling (mouse wheel + two-finger trackpad)
        def on_mousewheel(event):
            if getattr(event, 'num', None) == 4:
                step = -1
            elif getattr(event, 'num', None) == 5:
                step = 1
            else:
                delta = getattr(event, 'delta', 0)
                if delta == 0:
                    return "break"
                step = -1 if delta > 0 else 1
            canvas.yview_scroll(step, "units")
            return "break"

        def bind_mousewheel(_event=None):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            canvas.bind_all("<Button-4>", on_mousewheel)
            canvas.bind_all("<Button-5>", on_mousewheel)

        def unbind_mousewheel(_event=None):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        for widget in (tab, canvas, scrollable_frame):
            widget.bind("<Enter>", bind_mousewheel)
            widget.bind("<Leave>", unbind_mousewheel)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        main = tk.Frame(scrollable_frame, bg=self.COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Title
        title_frame = tk.Frame(main, bg=self.COLORS['bg_dark'])
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="⚙️ Settings & Preferences",
            font=('Segoe UI', 20, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text']
        ).pack(side='left')
        
        # === THEME SETTINGS ===
        theme_section = tk.Frame(main, bg=self.COLORS['bg_medium'])
        theme_section.pack(fill='x', pady=(0, 15))
        
        tk.Frame(theme_section, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        theme_content = tk.Frame(theme_section, bg=self.COLORS['bg_medium'])
        theme_content.pack(fill='x', padx=25, pady=20)
        
        tk.Label(
            theme_content,
            text="Appearance",
            font=('Segoe UI', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 15))
        
        # Theme selection
        theme_frame = tk.Frame(theme_content, bg=self.COLORS['bg_medium'])
        theme_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            theme_frame,
            text="Theme:",
            font=('Segoe UI', 11),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(side='left', padx=(0, 15))
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        
        dark_btn = tk.Radiobutton(
            theme_frame,
            text="🌙 Dark Mode",
            variable=self.theme_var,
            value='dark',
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            selectcolor=self.COLORS['bg_light'],
            activebackground=self.COLORS['bg_medium'],
            activeforeground=self.COLORS['accent'],
            command=lambda: self.change_theme('dark')
        )
        dark_btn.pack(side='left', padx=(0, 15))
        
        light_btn = tk.Radiobutton(
            theme_frame,
            text="☀️ Light Mode",
            variable=self.theme_var,
            value='light',
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            selectcolor=self.COLORS['bg_light'],
            activebackground=self.COLORS['bg_medium'],
            activeforeground=self.COLORS['accent'],
            command=lambda: self.change_theme('light')
        )
        light_btn.pack(side='left')
        
        # === MONITORING SETTINGS ===
        monitor_section = tk.Frame(main, bg=self.COLORS['bg_medium'])
        monitor_section.pack(fill='x', pady=(0, 15))
        
        tk.Frame(monitor_section, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        monitor_content = tk.Frame(monitor_section, bg=self.COLORS['bg_medium'])
        monitor_content.pack(fill='x', padx=25, pady=20)
        
        tk.Label(
            monitor_content,
            text="📊 Monitoring Settings",
            font=('Segoe UI', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 15))
        
        # Update interval
        interval_frame = tk.Frame(monitor_content, bg=self.COLORS['bg_medium'])
        interval_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            interval_frame,
            text="Update Interval:",
            font=('Segoe UI', 11),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(side='left', padx=(0, 15))
        
        self.interval_var = tk.StringVar(value=str(self.update_interval))
        interval_combo = ttk.Combobox(
            interval_frame,
            textvariable=self.interval_var,
            values=['250', '500', '1000', '2000', '5000'],
            state='readonly',
            width=10
        )
        interval_combo.pack(side='left', padx=(0, 10))
        
        tk.Label(
            interval_frame,
            text="milliseconds",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        ).pack(side='left')
        
        # Auto-start
        self.auto_start_var = tk.BooleanVar(value=self.auto_start_monitoring)
        auto_check = tk.Checkbutton(
            monitor_content,
            text="Auto-start monitoring on launch",
            variable=self.auto_start_var,
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            selectcolor=self.COLORS['bg_light'],
            activebackground=self.COLORS['bg_medium'],
            activeforeground=self.COLORS['accent']
        )
        auto_check.pack(anchor='w', pady=(0, 10))
        
        # Notifications
        self.notif_var = tk.BooleanVar(value=self.show_notifications)
        notif_check = tk.Checkbutton(
            monitor_content,
            text="Show system notifications for alerts",
            variable=self.notif_var,
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            selectcolor=self.COLORS['bg_light'],
            activebackground=self.COLORS['bg_medium'],
            activeforeground=self.COLORS['accent']
        )
        notif_check.pack(anchor='w')
        
        # === DATA SETTINGS ===
        data_section = tk.Frame(main, bg=self.COLORS['bg_medium'])
        data_section.pack(fill='x', pady=(0, 15))
        
        tk.Frame(data_section, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        data_content = tk.Frame(data_section, bg=self.COLORS['bg_medium'])
        data_content.pack(fill='x', padx=25, pady=20)
        
        tk.Label(
            data_content,
            text="💾 Data Management",
            font=('Segoe UI', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 15))
        
        # Buttons frame
        buttons_frame = tk.Frame(data_content, bg=self.COLORS['bg_medium'])
        buttons_frame.pack(fill='x', pady=(0, 10))
        
        # Export graph data button
        export_btn = tk.Button(
            buttons_frame,
            text="📊 Export Graph Data",
            font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['accent'],
            fg=self.COLORS['bg_dark'],
            activebackground=self.COLORS['bg_light'],
            relief='flat',
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.export_graph_data
        )
        export_btn.pack(side='left', padx=(0, 10))
        
        # Save graph image button
        save_img_btn = tk.Button(
            buttons_frame,
            text="📸 Save Graph Images",
            font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['success'],
            fg=self.COLORS['text'],
            activebackground=self.COLORS['bg_light'],
            relief='flat',
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.save_graph_images
        )
        save_img_btn.pack(side='left', padx=(0, 10))
        
        # Print report button
        print_btn = tk.Button(
            buttons_frame,
            text="🖨️ Print Report",
            font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['warning'],
            fg=self.COLORS['bg_dark'],
            activebackground=self.COLORS['bg_light'],
            relief='flat',
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.print_performance_report
        )
        print_btn.pack(side='left')
        
        # Clear data button
        clear_btn = tk.Button(
            data_content,
            text="🗑️ Clear All Graph Data",
            font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text'],
            activebackground=self.COLORS['bg_medium'],
            relief='flat',
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.clear_graph_data
        )
        clear_btn.pack(anchor='w', pady=(10, 10))
        
        tk.Label(
            data_content,
            text="Export data to CSV, save graphs as images, or print performance reports",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        ).pack(anchor='w')
        
        # === ACCOUNT SETTINGS ===
        account_section = tk.Frame(main, bg=self.COLORS['bg_medium'])
        account_section.pack(fill='x', pady=(0, 15))
        
        tk.Frame(account_section, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        account_content = tk.Frame(account_section, bg=self.COLORS['bg_medium'])
        account_content.pack(fill='x', padx=25, pady=20)
        
        tk.Label(
            account_content,
            text="👤 Account",
            font=('Segoe UI', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 15))
        
        # User info
        user_info_frame = tk.Frame(account_content, bg=self.COLORS['bg_light'], relief='flat')
        user_info_frame.pack(fill='x', pady=(0, 15))
        
        user_content = tk.Frame(user_info_frame, bg=self.COLORS['bg_light'])
        user_content.pack(fill='x', padx=15, pady=15)
        
        tk.Label(
            user_content,
            text=f"👤 Current User: {os.getlogin() if hasattr(os, 'getlogin') else 'User'}",
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 5))
        
        import platform
        tk.Label(
            user_content,
            text=f"💻 System: {platform.system()} {platform.release()}",
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text']
        ).pack(anchor='w')
        
        # Logout button
        logout_btn = tk.Button(
            account_content,
            text="🚪 Logout & Exit",
            font=('Segoe UI', 11, 'bold'),
            bg=self.COLORS['danger'],
            fg=self.COLORS['text'],
            activebackground='#cc0000',
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.logout_confirm
        )
        logout_btn.pack(anchor='w')
        
        # === ABOUT SECTION ===
        about_section = tk.Frame(main, bg=self.COLORS['bg_medium'])
        about_section.pack(fill='x', pady=(0, 15))
        
        tk.Frame(about_section, bg=self.COLORS['accent'], height=3).pack(fill='x')
        
        about_content = tk.Frame(about_section, bg=self.COLORS['bg_medium'])
        about_content.pack(fill='x', padx=25, pady=20)
        
        tk.Label(
            about_content,
            text="ℹ️ About",
            font=('Segoe UI', 14, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 15))
        
        tk.Label(
            about_content,
            text="System Monitor - FYP Project",
            font=('Segoe UI', 11, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 5))
        
        tk.Label(
            about_content,
            text="Version 1.0.0",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            about_content,
            text="Created by: Ali Mehdi, Bilal Latif, Ali Haider",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        ).pack(anchor='w', pady=(0, 5))
        
        tk.Label(
            about_content,
            text="Advisor: Prof. M Asif",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        ).pack(anchor='w', pady=(0, 5))
        
        tk.Label(
            about_content,
            text="Govt. Islamia Graduate College, Gujranwala",
            font=('Segoe UI', 9),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        ).pack(anchor='w')
        
        # Save settings button
        save_frame = tk.Frame(main, bg=self.COLORS['bg_dark'])
        save_frame.pack(fill='x', pady=(20, 0))
        
        save_btn = tk.Button(
            save_frame,
            text="💾 Save Settings",
            font=('Segoe UI', 12, 'bold'),
            bg=self.COLORS['accent'],
            fg=self.COLORS['bg_dark'],
            activebackground=self.COLORS['bg_light'],
            relief='flat',
            padx=30,
            pady=12,
            cursor='hand2',
            command=self.save_settings
        )
        save_btn.pack(side='right')

    def change_theme(self, theme):
        """Change application theme"""
        from tkinter import messagebox
        
        result = messagebox.askyesno(
            "Change Theme",
            f"Switch to {theme} mode?\n\nNote: This will require restarting the application to fully apply.",
            icon='question'
        )
        
        if result:
            self.current_theme = theme
            if theme == 'light':
                self.COLORS = self.COLORS_LIGHT.copy()
            else:
                # Reset to original dark colors
                self.COLORS = {
                    'bg_dark': '#1a1a2e',
                    'bg_medium': '#16213e',
                    'bg_light': '#0f3460',
                    'accent': '#00d4ff',
                    'text': '#ffffff',
                    'text_dim': '#94a3b8',
                    'cpu_color': '#00ff88',
                    'mem_color': '#ff6b6b',
                    'disk_color': '#ffd93d',
                    'net_down_color': '#00d4ff',
                    'net_up_color': '#ff4757',
                    'success': '#00ff88',
                    'warning': '#ffd93d',
                    'danger': '#ff6b6b',
                    'graph_bg': '#0f1419',
                    'grid_color': '#2a3441'
                }
            
            messagebox.showinfo(
                "Theme Changed",
                "Theme preference saved!\n\nPlease restart the application for changes to take full effect."
            )

    def clear_graph_data(self):
        """Clear all graph data"""
        from tkinter import messagebox
        
        result = messagebox.askyesno(
            "Clear Data",
            "Clear all graph history?\n\nThis will reset all graphs to empty.",
            icon='warning'
        )
        
        if result:
            # Clear all data queues
            self.cpu_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
            self.mem_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
            self.disk_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
            self.net_down_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
            self.net_up_data = deque([0] * self.max_data_points, maxlen=self.max_data_points)
            
            messagebox.showinfo("Data Cleared", "All graph data has been cleared!")


    def save_settings(self):
        """Save current settings and persist to database for logged-in user."""
        from tkinter import messagebox

        try:
            self.update_interval = int(self.interval_var.get())
            self.auto_start_monitoring = self.auto_start_var.get()
            self.show_notifications = self.notif_var.get()
            self.current_theme = self.theme_var.get()

            if getattr(self, 'db_manager', None) and getattr(self, 'current_user', None):
                user_id = self.current_user.get('user_id') if isinstance(self.current_user, dict) else None
                if user_id:
                    ok, msg = self.db_manager.save_user_settings(
                        user_id=user_id,
                        theme=self.current_theme,
                        update_interval=self.update_interval,
                        auto_start_monitoring=self.auto_start_monitoring,
                        show_notifications=self.show_notifications,
                    )
                    if not ok:
                        messagebox.showerror('Error', f'Failed to save settings: {msg}')
                        return

            messagebox.showinfo(
                'Settings Saved',
                'Settings saved successfully!\n\nChanges are applied and will persist for this user.'
            )
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save settings: {e}')


    def logout_confirm(self):
        """Confirm logout and exit"""
        from tkinter import messagebox
        
        result = messagebox.askyesno(
            "Logout & Exit",
            "Are you sure you want to logout and exit the application?\n\nAll unsaved data will be lost.",
            icon='warning'
        )
        
        if result:
            self.running = False
            self.root.quit()
            self.root.destroy()

    def export_graph_data(self):
        """Export graph data to CSV file"""
        from tkinter import filedialog, messagebox
        import csv
        from datetime import datetime
        
        try:
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"system_monitor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if filename:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow(['Timestamp', 'CPU %', 'RAM %', 'Disk %', 'Download Mbps', 'Upload Mbps'])
                    
                    # Write data
                    for i in range(len(self.cpu_data)):
                        timestamp = i * 0.5  # seconds
                        writer.writerow([
                            f"{timestamp:.1f}s",
                            f"{self.cpu_data[i]:.2f}",
                            f"{self.mem_data[i]:.2f}",
                            f"{self.disk_data[i]:.2f}",
                            f"{self.net_down_data[i]:.2f}",
                            f"{self.net_up_data[i]:.2f}"
                        ])
                    
                    messagebox.showinfo(
                        "Export Successful",
                        f"Graph data exported successfully!\n\n"
                        f"File: {filename}\n"
                        f"Data points: {len(self.cpu_data)}"
                    )
        
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export data:\n{e}")

    def save_graph_images(self):
        """Save graph images as PNG files"""
        from tkinter import filedialog, messagebox
        from datetime import datetime
        import os
        
        try:
            # Ask for directory
            directory = filedialog.askdirectory(title="Select folder to save graph images")
            
            if directory:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                saved_files = []
                
                # Save each canvas as PostScript then convert to image
                canvases = [
                    ('CPU_Graph', self.cpu_canvas),
                    ('Memory_Graph', self.mem_canvas),
                    ('Disk_Graph', self.disk_canvas),
                    ('Network_Graph', self.net_canvas)
                ]
                
                for name, canvas in canvases:
                    try:
                        # Generate filename
                        ps_file = os.path.join(directory, f"{name}_{timestamp}.ps")
                        png_file = os.path.join(directory, f"{name}_{timestamp}.png")
                        
                        # Save as PostScript
                        canvas.postscript(file=ps_file, colormode='color')
                        
                        # Try to convert to PNG if PIL is available
                        try:
                            from PIL import Image
                            img = Image.open(ps_file)
                            img.save(png_file, 'PNG')
                            os.remove(ps_file)  # Remove PS file
                            saved_files.append(png_file)
                        except ImportError:
                            # PIL not available, keep PostScript file
                            saved_files.append(ps_file)
                    
                    except Exception as e:
                        print(f"Failed to save {name}: {e}")
                
                if saved_files:
                    messagebox.showinfo(
                        "Images Saved",
                        f"Graph images saved successfully!\n\n"
                        f"Location: {directory}\n"
                        f"Files saved: {len(saved_files)}\n\n"
                        f"Note: Images saved as PostScript (.ps) files.\n"
                        f"Install Pillow for PNG: pip install Pillow"
                    )
                else:
                    messagebox.showwarning("Save Failed", "No images were saved.")
        
        except Exception as e:
            messagebox.showerror("Save Failed", f"Failed to save images:\n{e}")

    def print_performance_report(self):
        """Generate and print/save performance report"""
        from tkinter import filedialog, messagebox
        from datetime import datetime
        
        try:
            # Calculate statistics
            cpu_avg = sum(self.cpu_data) / len(self.cpu_data) if self.cpu_data else 0
            cpu_max = max(self.cpu_data) if self.cpu_data else 0
            cpu_min = min(self.cpu_data) if self.cpu_data else 0
            
            mem_avg = sum(self.mem_data) / len(self.mem_data) if self.mem_data else 0
            mem_max = max(self.mem_data) if self.mem_data else 0
            mem_min = min(self.mem_data) if self.mem_data else 0
            
            disk_avg = sum(self.disk_data) / len(self.disk_data) if self.disk_data else 0
            disk_max = max(self.disk_data) if self.disk_data else 0
            disk_min = min(self.disk_data) if self.disk_data else 0
            
            net_down_avg = sum(self.net_down_data) / len(self.net_down_data) if self.net_down_data else 0
            net_down_max = max(self.net_down_data) if self.net_down_data else 0
            
            net_up_avg = sum(self.net_up_data) / len(self.net_up_data) if self.net_up_data else 0
            net_up_max = max(self.net_up_data) if self.net_up_data else 0
            
            # Generate report
            report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     SYSTEM PERFORMANCE REPORT                            ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}               ║
║  Monitoring Period: Last 30 seconds ({len(self.cpu_data)} data points)   ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  CPU USAGE                                                               ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Average:    {cpu_avg:6.2f}%                                             ║
║  Maximum:    {cpu_max:6.2f}%                                             ║
║  Minimum:    {cpu_min:6.2f}%                                             ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  MEMORY USAGE                                                            ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Average:    {mem_avg:6.2f}%                                             ║
║  Maximum:    {mem_max:6.2f}%                                             ║
║  Minimum:    {mem_min:6.2f}%                                             ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  DISK USAGE                                                              ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Average:    {disk_avg:6.2f}%                                            ║
║  Maximum:    {disk_max:6.2f}%                                            ║
║  Minimum:    {disk_min:6.2f}%                                            ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  NETWORK USAGE                                                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Download:                                                               ║
║    Average:  {net_down_avg:6.2f} Mbps                                    ║
║    Peak:     {net_down_max:6.2f} Mbps                                    ║
║                                                                          ║
║  Upload:                                                                 ║
║    Average:  {net_up_avg:6.2f} Mbps                                      ║
║    Peak:     {net_up_max:6.2f} Mbps                                      ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  SYSTEM STATUS                                                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║  CPU Status:     {"CRITICAL" if cpu_avg > 80 else "HIGH" if cpu_avg > 50 else "NORMAL":<10}                                                   ║
║  Memory Status:  {"CRITICAL" if mem_avg > 80 else "HIGH" if mem_avg > 50 else "NORMAL":<10}                                                   ║
║  Disk Status:    {"CRITICAL" if disk_avg > 90 else "HIGH" if disk_avg > 70 else "NORMAL":<10}                                                   ║
║  Network Status: {"HEAVY" if net_down_avg + net_up_avg > 50 else "ACTIVE" if net_down_avg + net_up_avg > 10 else "LIGHT":<10}                                                   ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

Generated by System Monitor - FYP Project
Team: Ali Mehdi, Bilal Latif, Ali Haider
Advisor: Prof. M Asif
"""
            # Ask where to save
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            ) 
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                messagebox.showinfo(
                    "Report Saved",
                    f"Performance report saved successfully!\n\n"
                    f"File: {filename}\n\n"
                    f"You can now:\n"
                    f"• Open it in Notepad\n"
                    f"• Print it from any text editor\n"
                    f"• Share it via email"
                )
                # Ask if user wants to open the file
                if messagebox.askyesno("Open File", "Do you want to open the report now?"):
                    try:
                        import subprocess
                        import platform
                        if platform.system() == 'Windows':
                            os.startfile(filename)
                        elif platform.system() == 'Darwin':  # macOS
                            subprocess.call(['open', filename])
                        else:  # Linux
                            subprocess.call(['xdg-open', filename])
                    except Exception as e:
                        print(f"Could not open file: {e}")
        except Exception as e:
            messagebox.showerror("Report Failed", f"Failed to generate report:\n{e}")
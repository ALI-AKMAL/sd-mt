import tkinter as tk
from tkinter import ttk
import threading
class ProcessTabMixin:
    def create_process_tab(self):
        """Create process manager tab."""
        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='Processes')

        # State used to keep background work controlled and responsive.
        self._process_search_after_id = None
        self._process_request_id = 0
        self._process_loading = False

        main = tk.Frame(tab, bg=self.COLORS['bg_dark'])
        main.pack(fill='both', expand=True, padx=20, pady=20)

        controls = tk.Frame(main, bg=self.COLORS['bg_dark'])
        controls.pack(fill='x', pady=(0, 15))

        tk.Label(
            controls,
            text='Process Manager',
            font=('Segoe UI', 18, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text']
        ).pack(side='left')

        self.process_refresh_btn = tk.Button(
            controls,
            text='Refresh',
            font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['accent'],
            fg=self.COLORS['bg_dark'],
            activebackground=self.COLORS['bg_light'],
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.refresh_processes
        )
        self.process_refresh_btn.pack(side='right', padx=(10, 0))

        tk.Label(
            controls,
            text='Sort by:',
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text']
        ).pack(side='right', padx=(20, 5))

        self.sort_var = tk.StringVar(value='cpu')
        sort_menu = ttk.Combobox(
            controls,
            textvariable=self.sort_var,
            values=['cpu', 'memory', 'name', 'pid'],
            state='readonly',
            width=10
        )
        sort_menu.pack(side='right')
        sort_menu.bind('<<ComboboxSelected>>', lambda e: self.refresh_processes())

        search_frame = tk.Frame(main, bg=self.COLORS['bg_dark'])
        search_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            search_frame,
            text='Search:',
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text']
        ).pack(side='left', padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.schedule_search_processes())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            insertbackground=self.COLORS['accent'],
            relief='flat',
            width=30
        )
        search_entry.pack(side='left', ipady=5, ipadx=10)

        summary_frame = tk.Frame(main, bg=self.COLORS['bg_medium'])
        summary_frame.pack(fill='x', pady=(0, 15))
        tk.Frame(summary_frame, bg=self.COLORS['accent'], height=2).pack(fill='x')

        summary_content = tk.Frame(summary_frame, bg=self.COLORS['bg_medium'])
        summary_content.pack(fill='x', padx=20, pady=12)

        self.process_summary_label = tk.Label(
            summary_content,
            text='Loading processes...',
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        )
        self.process_summary_label.pack(anchor='w')

        list_frame = tk.Frame(main, bg=self.COLORS['bg_medium'])
        list_frame.pack(fill='both', expand=True)
        tk.Frame(list_frame, bg=self.COLORS['accent'], height=3).pack(fill='x')

        header_frame = tk.Frame(list_frame, bg=self.COLORS['bg_light'])
        header_frame.pack(fill='x', padx=2, pady=2)

        headers = [
            ('PID', 8),
            ('Process Name', 30),
            ('CPU %', 10),
            ('Memory (MB)', 12),
            ('Status', 12),
            ('', 20),
        ]
        for header, width in headers:
            tk.Label(
                header_frame,
                text=header,
                font=('Segoe UI', 9, 'bold'),
                bg=self.COLORS['bg_light'],
                fg=self.COLORS['accent'],
                width=width,
                anchor='w'
            ).pack(side='left', padx=5)

        list_container = tk.Frame(list_frame, bg=self.COLORS['bg_medium'])
        list_container.pack(fill='both', expand=True, padx=2, pady=2)

        canvas = tk.Canvas(list_container, bg=self.COLORS['bg_medium'], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient='vertical', command=canvas.yview)
        self.process_list_frame = tk.Frame(canvas, bg=self.COLORS['bg_medium'])
        window = canvas.create_window((0, 0), window=self.process_list_frame, anchor='nw')

        self.process_list_frame.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda event: canvas.itemconfig(window, width=event.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_mousewheel(event):
            if getattr(event, 'num', None) == 4:
                step = -1
            elif getattr(event, 'num', None) == 5:
                step = 1
            else:
                delta = getattr(event, 'delta', 0)
                if delta == 0:
                    return 'break'
                step = -1 if delta > 0 else 1
            canvas.yview_scroll(step, 'units')
            return 'break'

        def bind_mousewheel(_event=None):
            canvas.bind_all('<MouseWheel>', on_mousewheel)
            canvas.bind_all('<Button-4>', on_mousewheel)
            canvas.bind_all('<Button-5>', on_mousewheel)

        def unbind_mousewheel(_event=None):
            canvas.unbind_all('<MouseWheel>')
            canvas.unbind_all('<Button-4>')
            canvas.unbind_all('<Button-5>')

        for widget in (tab, canvas, self.process_list_frame):
            widget.bind('<Enter>', bind_mousewheel)
            widget.bind('<Leave>', unbind_mousewheel)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.load_processes()

    def schedule_search_processes(self):
        """Debounce search input to prevent lag while typing."""
        if self._process_search_after_id:
            self.root.after_cancel(self._process_search_after_id)
        self._process_search_after_id = self.root.after(300, self.search_processes)

    def load_processes(self):
        """Load and display processes."""
        if self._process_loading:
            return

        self._process_loading = True
        self._process_request_id += 1
        request_id = self._process_request_id

        self.process_summary_label.config(text='Loading processes...')
        self.process_refresh_btn.config(state='disabled', text='Refreshing...')

        for widget in self.process_list_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.process_list_frame,
            text='Loading processes... This may take a few seconds...',
            font=('Segoe UI', 12),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        ).pack(pady=50)

        def load_thread():
            try:
                sort_by = self.sort_var.get()
                processes = self.process_manager.get_all_processes(sort_by=sort_by, limit=30)
                summary = self.process_manager.get_system_summary()
                self.root.after(0, self.display_processes, processes, summary, request_id)
            except Exception as e:
                self.root.after(0, self._handle_process_error, f'Error loading processes: {e}')

        threading.Thread(target=load_thread, daemon=True).start()

    def _handle_process_error(self, error_msg):
        self.process_summary_label.config(text=error_msg)
        self._finish_process_loading()

    def _finish_process_loading(self):
        self._process_loading = False
        self.process_refresh_btn.config(state='normal', text='Refresh')

    def display_processes(self, processes, summary, request_id=None):
        """Display process list."""
        if request_id is not None and request_id != self._process_request_id:
            return

        summary_text = f"Total: {summary['total']} | Running: {summary['running']} | Sleeping: {summary['sleeping']}"
        self.process_summary_label.config(text=summary_text)

        for widget in self.process_list_frame.winfo_children():
            widget.destroy()

        self._render_process_rows(processes, 0)

    def _render_process_rows(self, processes, start_index):
        """Render rows in chunks to keep UI smooth."""
        chunk_size = 50
        end_index = min(start_index + chunk_size, len(processes))

        for i in range(start_index, end_index):
            self.create_process_row(processes[i], i)

        if end_index < len(processes):
            self.root.after(1, self._render_process_rows, processes, end_index)
        else:
            self._finish_process_loading()

    def create_process_row(self, proc, index):
        """Create a single process row."""
        bg_color = self.COLORS['bg_light'] if index % 2 == 0 else self.COLORS['bg_medium']

        row = tk.Frame(self.process_list_frame, bg=bg_color)
        row.pack(fill='x', pady=1)

        tk.Label(
            row,
            text=str(proc['pid']),
            font=('Segoe UI', 9),
            bg=bg_color,
            fg=self.COLORS['text'],
            width=8,
            anchor='w'
        ).pack(side='left', padx=5)

        name_text = proc['name']
        if proc['is_critical']:
            name_text = f"! {name_text}"

        tk.Label(
            row,
            text=name_text,
            font=('Segoe UI', 9, 'bold' if proc['is_critical'] else 'normal'),
            bg=bg_color,
            fg=self.COLORS['warning'] if proc['is_critical'] else self.COLORS['text'],
            width=30,
            anchor='w'
        ).pack(side='left', padx=5)

        cpu_color = self.COLORS['success']
        if proc['cpu_percent'] > 50:
            cpu_color = self.COLORS['warning']
        if proc['cpu_percent'] > 80:
            cpu_color = self.COLORS['danger']

        tk.Label(
            row,
            text=f"{proc['cpu_percent']:.1f}%",
            font=('Segoe UI', 9),
            bg=bg_color,
            fg=cpu_color,
            width=10,
            anchor='w'
        ).pack(side='left', padx=5)

        tk.Label(
            row,
            text=f"{proc['memory_mb']:.1f}",
            font=('Segoe UI', 9),
            bg=bg_color,
            fg=self.COLORS['text'],
            width=12,
            anchor='w'
        ).pack(side='left', padx=5)

        tk.Label(
            row,
            text=proc['status'],
            font=('Segoe UI', 9),
            bg=bg_color,
            fg=self.COLORS['text_dim'],
            width=12,
            anchor='w'
        ).pack(side='left', padx=5)

        tk.Button(
            row,
            text='End Process',
            font=('Segoe UI', 8, 'bold'),
            bg=self.COLORS['danger'],
            fg=self.COLORS['text'],
            activebackground=self.COLORS['warning'],
            relief='flat',
            padx=10,
            pady=4,
            cursor='hand2',
            command=lambda: self.kill_process(proc['pid'], proc['name'], proc['is_critical'])
        ).pack(side='left', padx=5)

    def kill_process(self, pid, name, is_critical):
        """Kill a process with confirmation."""
        from tkinter import messagebox

        if is_critical:
            result = messagebox.askyesno(
                'Critical Process Warning',
                (
                    f"WARNING: '{name}' is a critical system process!\n\n"
                    'Terminating this process may cause system instability or crash.\n\n'
                    'Are you absolutely sure you want to end this process?'
                ),
                icon='warning'
            )
        else:
            result = messagebox.askyesno(
                'Confirm Process Termination',
                (
                    'Are you sure you want to end process:\n\n'
                    f'Name: {name}\n'
                    f'PID: {pid}\n\n'
                    'This action cannot be undone.'
                ),
                icon='question'
            )

        if not result:
            self.show_notification('Process termination cancelled', error=False)
            return

        def kill_thread():
            result_data = self.process_manager.terminate_process(pid)
            self.root.after(0, self.handle_kill_result, result_data)

        threading.Thread(target=kill_thread, daemon=True).start()

    def handle_kill_result(self, result):
        """Handle process termination result."""
        if result['success']:
            self.show_notification('[OK] ' + result['message'], error=False)
            self.root.after(800, self.refresh_processes)
        else:
            self.show_notification('[X] ' + result['message'], error=True)

    def refresh_processes(self):
        """Refresh process list."""
        self.load_processes()

    def search_processes(self):
        """Search and filter processes."""
        self._process_search_after_id = None
        query = self.search_var.get().strip()

        if not query:
            self.refresh_processes()
            return

        self._process_request_id += 1
        request_id = self._process_request_id

        self.process_summary_label.config(text=f"Searching: {query}")

        def search_thread():
            try:
                results = self.process_manager.search_processes(query)
                summary = self.process_manager.get_system_summary()
                self.root.after(0, self.display_processes, results, summary, request_id)
            except Exception as e:
                self.root.after(0, self._handle_process_error, f'Search error: {e}')

        threading.Thread(target=search_thread, daemon=True).start()
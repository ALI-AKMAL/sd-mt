import tkinter as tk
import time
class KeyboardTabMixin:
    def create_keyboard_tab(self):
        # ── Track which keys have been pressed ──────────────────────────
        self.tested_keys = set()      # keys the user has pressed at least once
        self.key_buttons = {}         # keysym -> tk.Button widget on the keyboard

        # ── Create the tab and add it to the notebook ────────────────────
        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='Keyboard Test')

        # ── Title ────────────────────────────────────────────────────────
        tk.Label(
            tab,
            text='Keyboard Tester',
            font=('Segoe UI', 18, 'bold'),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text']
        ).pack(pady=(20, 5))

        tk.Label(
            tab,
            text='Press any key on your keyboard — it will light up green below.',
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_dim']
        ).pack(pady=(0, 15))

        # ── Info bar (last key + keys tested count) ──────────────────────
        info_frame = tk.Frame(tab, bg=self.COLORS['bg_medium'])
        info_frame.pack(fill='x', padx=30, pady=(0, 15))
        tk.Frame(info_frame, bg=self.COLORS['accent'], height=3).pack(fill='x')

        info_inner = tk.Frame(info_frame, bg=self.COLORS['bg_medium'])
        info_inner.pack(fill='x', padx=20, pady=12)

        # Last key pressed
        tk.Label(
            info_inner,
            text='Last Key Pressed:',
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        ).pack(side='left')

        self.last_key_label = tk.Label(
            info_inner,
            text='None',
            font=('Segoe UI', 12, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['accent'],
            width=12
        )
        self.last_key_label.pack(side='left', padx=(5, 30))

        # Keys tested count
        tk.Label(
            info_inner,
            text='Keys Tested:',
            font=('Segoe UI', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim']
        ).pack(side='left')

        self.keys_tested_label = tk.Label(
            info_inner,
            text='0',
            font=('Segoe UI', 12, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['accent'],
            width=5
        )
        self.keys_tested_label.pack(side='left', padx=(5, 0))

        # ── Visual keyboard ───────────────────────────────────────────────
        keyboard_frame = tk.Frame(tab, bg=self.COLORS['bg_dark'])
        keyboard_frame.pack(pady=(0, 15))

        # Each row is a list of (display text, keysym)
        # keysym is what tkinter gives us in event.keysym
        keyboard_rows = [
            # Row 1 — Function keys
            [('Esc','Escape'),('F1','F1'),('F2','F2'),('F3','F3'),('F4','F4'),
             ('F5','F5'),('F6','F6'),('F7','F7'),('F8','F8'),
             ('F9','F9'),('F10','F10'),('F11','F11'),('F12','F12')],
            # Row 2 — Numbers
            [('`','grave'),('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),
             ('6','6'),('7','7'),('8','8'),('9','9'),('0','0'),
             ('-','minus'),('=','equal'),('Bksp','BackSpace')],
            # Row 3 — QWERTY
            [('Tab','Tab'),('Q','q'),('W','w'),('E','e'),('R','r'),('T','t'),
             ('Y','y'),('U','u'),('I','i'),('O','o'),('P','p'),
             ('[','bracketleft'),(']','bracketright'),('\\','backslash')],
            # Row 4 — ASDF
            [('Caps','Caps_Lock'),('A','a'),('S','s'),('D','d'),('F','f'),('G','g'),
             ('H','h'),('J','j'),('K','k'),('L','l'),(';','semicolon'),
             ("'",'apostrophe'),('Enter','Return')],
            # Row 5 — ZXCV
            [('Shift','Shift_L'),('Z','z'),('X','x'),('C','c'),('V','v'),('B','b'),
             ('N','n'),('M','m'),(',','comma'),('.','period'),('/','slash'),
             ('Shift','Shift_R')],
            # Row 6 — Bottom
            [('Ctrl','Control_L'),('Alt','Alt_L'),
             ('Space','space'),
             ('Alt','Alt_R'),('Ctrl','Control_R')],
        ]

        for row in keyboard_rows:
            row_frame = tk.Frame(keyboard_frame, bg=self.COLORS['bg_dark'])
            row_frame.pack(pady=2)

            for display_text, keysym in row:
                # Make spacebar wider
                if keysym == 'space':
                    btn_width = 50
                elif keysym in ('BackSpace', 'Return', 'Shift_L', 'Shift_R',
                                'Caps_Lock', 'Tab'):
                    btn_width = 20
                else:
                    btn_width = 12
                btn = tk.Button(
                    row_frame,
                    text=display_text,
                    font=('Segoe UI', 8),
                    bg=self.COLORS['bg_light'],
                    fg=self.COLORS['text'],
                    relief='flat',
                    width=btn_width,
                    pady=6,
                    cursor='hand2'
                )
                btn.pack(side='left', padx=2)
                # Save reference so we can change color when key is pressed
                self.key_buttons[keysym] = btn
        # ── Reset button ──────────────────────────────────────────────────
        tk.Button(
            tab,
            text='Reset',
            font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['bg_light'],
            fg=self.COLORS['text'],
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.reset_keyboard_test
        ).pack(pady=(0, 10))
        # ── Recent keys log ───────────────────────────────────────────────
        log_frame = tk.Frame(tab, bg=self.COLORS['bg_medium'])
        log_frame.pack(fill='x', padx=30, pady=(0, 20))
        tk.Frame(log_frame, bg=self.COLORS['accent'], height=3).pack(fill='x')
        log_inner = tk.Frame(log_frame, bg=self.COLORS['bg_medium'])
        log_inner.pack(fill='x', padx=20, pady=12)
        tk.Label(
            log_inner,
            text='Recent Keys:',
            font=('Segoe UI', 10, 'bold'),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text']
        ).pack(anchor='w', pady=(0, 6))
        self.key_log_label = tk.Label(
            log_inner,
            text='—',
            font=('Consolas', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_dim'],
            anchor='w',
            justify='left',
            wraplength=800
        )
        self.key_log_label.pack(anchor='w')
        self.key_log_list = []   # stores last 20 key names
        # ── Bind keyboard events to the window ───────────────────────────
        self.root.bind('<KeyPress>', self.on_key_press)
    # ── Called every time a key is pressed ───────────────────────────────
    def on_key_press(self, event):
        sym = event.keysym
        # Update last key label
        self.last_key_label.config(text=sym)
        # Light up the key button green
        if sym in self.key_buttons:
            self.key_buttons[sym].config(
                bg=self.COLORS.get('success', '#00ff88'),
                fg=self.COLORS['bg_dark']
            )
        # Add to tested set and update counter
        self.tested_keys.add(sym)
        self.keys_tested_label.config(text=str(len(self.tested_keys)))
        # Add to recent keys log (keep last 20)
        self.key_log_list.append(sym)
        if len(self.key_log_list) > 20:
            self.key_log_list.pop(0)
        self.key_log_label.config(text='  '.join(self.key_log_list))
    # ── Reset everything back to default ─────────────────────────────────
    def reset_keyboard_test(self):
        # Reset all key buttons back to original color
        for sym, btn in self.key_buttons.items():
            btn.config(
                bg=self.COLORS['bg_light'],
                fg=self.COLORS['text']
            )
        # Clear all tracking data
        self.tested_keys.clear()
        self.key_log_list.clear()
        # Reset labels
        self.last_key_label.config(text='None')
        self.keys_tested_label.config(text='0')
        self.key_log_label.config(text='—')
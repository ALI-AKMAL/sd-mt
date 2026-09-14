import tkinter as tk
class KeyboardTabMixin:
    def create_keyboard_tab(self):

        self.key_buttons = {}

        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='Keyboard Test')

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

        # ── Visual keyboard ───────────────────────────────────────────────
        keyboard_frame = tk.Frame(tab, bg=self.COLORS['bg_dark'])
        keyboard_frame.pack(pady=(0, 15))

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
                    pady=10,
                    cursor='hand2'
                )
                btn.pack(side='left', padx=2)
                # Save reference so we can change color when key is pressed
                self.key_buttons[keysym] = btn

        # ── Bind keyboard events to the window ───────────────────────────
        self.root.bind('<KeyPress>', self.on_key_press)

    # ── Called every time a key is pressed ───────────────────────────────
    def on_key_press(self, event):
        sym = event.keysym
        # Light up the key button green
        if sym in self.key_buttons:
            self.key_buttons[sym].config(
                bg=self.COLORS.get('success', '#00ff88'),
                fg=self.COLORS['bg_dark']
            )
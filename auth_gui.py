import tkinter from tk
from tkinter import messagebox
from database_module import DatabaseManager
class AuthenticationGUI:
    def __init__(self, on_login_success=None):
        self.root = tk.Tk()
        self.root.title("System Monitor - Authentication")
        # 14-inch friendly size
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        self.db = DatabaseManager()
        self.current_user = None
        self.on_login_success = on_login_success
        self.colors = {
            'bg': '#1a1a2e',
            'card': '#16213e',
            'accent': '#00d4ff',
            'text': '#ffffff',
            'text_dim': '#94a3b8',
            'success': '#00ff88',
            'error': '#ff6b6b'
        }
        self.root.configure(bg=self.colors['bg'])
        self.show_login()
    def create_scrollable_page(self):
        self.clear_window()
        canvas = tk.Canvas(self.root, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=self.colors['bg'])
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        return frame
    def clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()
            
    # ---------- LOGIN ----------
    def show_login(self):
        main = self.create_scrollable_page()

        tk.Label(main, text="⚡", font=("Segoe UI", 48),
                 bg=self.colors['bg'], fg=self.colors['accent']).pack(pady=10)

        tk.Label(main, text="System Monitor", font=("Segoe UI", 24, "bold"),
                 bg=self.colors['bg'], fg=self.colors['text']).pack(anchor="w", padx=500)

        tk.Label(main, text="Login to your account",
                 bg=self.colors['bg'], fg=self.colors['text_dim']).pack(pady=10)

        card = tk.Frame(main, bg=self.colors['card'])
        card.pack(padx=40, pady=20, fill="x")

        form = tk.Frame(card, bg=self.colors['card'])
        form.pack(padx=30, pady=30)

        tk.Label(form, text="Username", bg=self.colors['card'],
                 fg=self.colors['text']).pack(anchor="w")

        self.login_username = tk.Entry(form, bg=self.colors['bg'],
                                       fg=self.colors['text'], relief="flat")
        self.login_username.pack(fill="x", ipady=8, pady=10)

        tk.Label(form, text="Password", bg=self.colors['card'],
                 fg=self.colors['text']).pack(anchor="w")

        self.login_password = tk.Entry(form, show="●",
                                       bg=self.colors['bg'], fg=self.colors['text'], relief="flat")
        self.login_password.pack(fill="x", ipady=8, pady=10)

        tk.Button(form, text="Login", bg=self.colors['accent'],
                  fg=self.colors['bg'], font=("Segoe UI", 12, "bold"),
                  command=self.handle_login).pack(fill="x", ipady=10, pady=10)

import tkinter as tk
from tkinter import messagebox, ttk
from database_module import DatabaseManager
SECURITY_QUESTIONS = [
    "What was the name of your first pet?",
    "What is your mother's maiden name?",
    "What was the name of your first school?",
    "What city were you born in?",
    "What was your childhood nickname?",
    "What is the name of your favorite childhood friend?",
    "What street did you grow up on?",
]
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
            'bg':       '#1a1a2e',
            'card':     '#16213e',
            'accent':   '#00d4ff',
            'text':     '#ffffff',
            'text_dim': '#94a3b8',
            'success':  '#00ff88',
            'error':    '#ff6b6b',
        }

        self.root.configure(bg=self.colors['bg'])
        self.show_login()

    # ---------- COMMON SCROLLABLE LAYOUT ----------
    def create_scrollable_page(self):
        self.clear_window()

        canvas = tk.Canvas(self.root, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)

        frame = tk.Frame(canvas, bg=self.colors['bg'])
        frame.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

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
                                       fg=self.colors['text'], relief="flat" , width=50)
        self.login_username.pack(fill="x", ipady=8, pady=10, padx=5)

        tk.Label(form, text="Password", bg=self.colors['card'],
                 fg=self.colors['text']).pack(anchor="w")

        self.login_password = tk.Entry(form, show="●",
                                       bg=self.colors['bg'], fg=self.colors['text'],
                                       relief="flat" , width=50)
        self.login_password.pack(fill="x", ipady=8, pady=10 , padx=5)
        
        "Enter key binding for login"
        
        self.login_username.bind("<Return>", lambda e: self.handle_login())   
        self.login_password.bind("<Return>", lambda e: self.handle_login())

        tk.Button(form, text="Login", bg=self.colors['accent'],
                  fg=self.colors['bg'], font=("Segoe UI", 12, "bold"),
                  command=self.handle_login).pack(fill="x", ipady=10, pady=10)

        # Forgot password link
        forgot_link = tk.Label(form, text="🔑 Forgot Password?",
                               font=("Segoe UI", 9, "underline"),
                               bg=self.colors['card'],
                               fg=self.colors['accent'],
                               cursor="hand2")
        forgot_link.pack(pady=(5, 0))
        forgot_link.bind("<Button-1>", lambda e: self.show_forgot_step1())

        tk.Button(main, text="Create New Account",
                  bg=self.colors['card'], fg=self.colors['accent'],
                  command=self.show_signup).pack(pady=10, ipadx=10, ipady=5)

    # ---------- SIGNUP (no email) ----------
    def show_signup(self):
        main = self.create_scrollable_page()

        tk.Label(main, text="Create Account",
                 font=("Segoe UI", 24, "bold"),
                 bg=self.colors['bg'], fg=self.colors['text']).pack(anchor="w", padx=500)

        card = tk.Frame(main, bg=self.colors['card'])
        card.pack(padx=40, pady=20, fill="x")

        form = tk.Frame(card, bg=self.colors['card'])
        form.pack(padx=30, pady=30)

        # --- Basic fields ---
        basic_fields = [
            ("Full Name","signup_fullname",  False),
            ("Username", "signup_username",  False),
            ("Password", "signup_password",  True),
            ("Confirm Password", "signup_confirm",   True),
        ]

        for label, var, is_password in basic_fields:
            tk.Label(form, text=label, bg=self.colors['card'],
                     fg=self.colors['text']).pack(anchor="w")
            entry = tk.Entry(form, bg=self.colors['bg'],
                             fg=self.colors['text'], relief="flat")
            if is_password:
                entry.config(show="●")
            entry.pack(fill="x", ipady=8, pady=8)
            setattr(self, var, entry)

        # --- Security question ---
        tk.Label(form,bg=self.colors['card'], fg=self.colors['text'] , width=50).pack(anchor="w", pady=(12, 0))

        self.signup_security_question = ttk.Combobox(
            form,
            values=SECURITY_QUESTIONS,
            state="readonly",
            font=("Segoe UI", 10),
        )
        self.signup_security_question.pack(fill="x", ipady=6, pady=8)
        self.signup_security_question.set(SECURITY_QUESTIONS[0])

        tk.Label(form, text="Security Answer",
                 bg=self.colors['card'], fg=self.colors['text']).pack(anchor="w")

        self.signup_security_answer = tk.Entry(form, bg=self.colors['bg'],
                                               fg=self.colors['text'], relief="flat")
        self.signup_security_answer.pack(fill="x", ipady=8, pady=8)

        tk.Button(form, text="Create Account",
                  bg=self.colors['accent'], fg=self.colors['bg'],
                  font=("Segoe UI", 12, "bold"),
                  command=self.handle_signup).pack(fill="x", ipady=10, pady=10)

        tk.Button(main, text="Back to Login",
                  fg=self.colors['accent'], bg=self.colors['bg'],
                  command=self.show_login).pack(pady=10)

    # ---------- FORGOT PASSWORD — STEP 1: enter username ----------
    def show_forgot_step1(self):
        """Step 1 — ask for username to look up the security question."""
        main = self.create_scrollable_page()

        tk.Label(main, text="🔑", font=("Segoe UI", 48),
                 bg=self.colors['bg'], fg=self.colors['accent']).pack(pady=10)

        tk.Label(main, text="Forgot Password",
                 font=("Segoe UI", 24, "bold"),
                 bg=self.colors['bg'], fg=self.colors['text']).pack(anchor="w", padx=500)

        tk.Label(main, text="Enter your username to retrieve your security question",
                 font=("Segoe UI", 10),
                 bg=self.colors['bg'], fg=self.colors['text_dim']).pack(pady=10)

        card = tk.Frame(main, bg=self.colors['card'])
        card.pack(padx=40, pady=20, fill="x")

        form = tk.Frame(card, bg=self.colors['card'])
        form.pack(padx=30, pady=30)

        tk.Label(form, text="Username", bg=self.colors['card'],
                 fg=self.colors['text']).pack(anchor="w")

        self.forgot_username = tk.Entry(form, bg=self.colors['bg'],
                                        fg=self.colors['text'], relief="flat")
        self.forgot_username.pack(fill="x", ipady=8, pady=10)

        tk.Button(form, text="Next →",
                  bg=self.colors['accent'], fg=self.colors['bg'],
                  font=("Segoe UI", 12, "bold"),
                  command=self.handle_forgot_step1).pack(fill="x", ipady=10, pady=10)

        tk.Button(main, text="← Back to Login",
                  bg=self.colors['card'], fg=self.colors['accent'],
                  command=self.show_login).pack(pady=10, ipadx=10, ipady=5)

    # ---------- FORGOT PASSWORD — STEP 2: answer question + new password ----------
    def show_forgot_step2(self, username, security_question):
        """Step 2 — show the security question and collect answer + new password."""
        main = self.create_scrollable_page()

        tk.Label(main, text="🔑", font=("Segoe UI", 48),
                 bg=self.colors['bg'], fg=self.colors['accent']).pack(pady=10)

        tk.Label(main, text="Reset Password",
                 font=("Segoe UI", 24, "bold"),
                 bg=self.colors['bg'], fg=self.colors['text']).pack(anchor="w", padx=500)

        tk.Label(main, text=f"Resetting password for:  {username}",
                 font=("Segoe UI", 10),
                 bg=self.colors['bg'], fg=self.colors['text_dim']).pack(pady=(5, 0))

        card = tk.Frame(main, bg=self.colors['card'])
        card.pack(padx=40, pady=20, fill="x")

        form = tk.Frame(card, bg=self.colors['card'])
        form.pack(padx=30, pady=30)

        # Display the security question (read-only)
        tk.Label(form, text="Your Security Question",
                 bg=self.colors['card'], fg=self.colors['text_dim'],
                 font=("Segoe UI", 9)).pack(anchor="w")

        tk.Label(form, text=security_question,
                 bg=self.colors['card'], fg=self.colors['accent'],
                 font=("Segoe UI", 11, "bold"),
                 wraplength=500, justify="left").pack(anchor="w", pady=(2, 14))

        # Answer field
        tk.Label(form, text="Your Answer",
                 bg=self.colors['card'], fg=self.colors['text']).pack(anchor="w")

        self.forgot_answer = tk.Entry(form, bg=self.colors['bg'],
                                      fg=self.colors['text'], relief="flat")
        self.forgot_answer.pack(fill="x", ipady=8, pady=8)

        # New password
        tk.Label(form, text="New Password",
                 bg=self.colors['card'], fg=self.colors['text']).pack(anchor="w")

        self.forgot_new_password = tk.Entry(form, show="●",
                                            bg=self.colors['bg'],
                                            fg=self.colors['text'], relief="flat")
        self.forgot_new_password.pack(fill="x", ipady=8, pady=8)

        # Confirm new password
        tk.Label(form, text="Confirm New Password",
                 bg=self.colors['card'], fg=self.colors['text']).pack(anchor="w")

        self.forgot_confirm_password = tk.Entry(form, show="●",
                                                bg=self.colors['bg'],
                                                fg=self.colors['text'], relief="flat")
        self.forgot_confirm_password.pack(fill="x", ipady=8, pady=8)

        # Store username for the action handler
        self._reset_username = username

        tk.Button(form, text="Reset Password",
                  bg=self.colors['success'], fg=self.colors['bg'],
                  font=("Segoe UI", 12, "bold"),
                  command=self.handle_forgot_step2).pack(fill="x", ipady=10, pady=10)

        tk.Button(main, text="← Back",
                  bg=self.colors['card'], fg=self.colors['accent'],
                  command=self.show_forgot_step1).pack(pady=10, ipadx=10, ipady=5)

    # ---------- ACTIONS ----------
    def handle_login(self):
        u = self.login_username.get().strip()
        p = self.login_password.get()
        if not u or not p:
            messagebox.showerror("Error", "Fill all fields")
            return

        success, msg, user = self.db.login_user(u, p)
        if success:
            self.current_user = user
            self.open_dashboard()
        else:
            messagebox.showerror("Login Failed", msg)

    def handle_signup(self):
        fullname  = self.signup_fullname.get().strip()
        username  = self.signup_username.get().strip()
        password  = self.signup_password.get()
        confirm   = self.signup_confirm.get()
        sec_q     = self.signup_security_question.get().strip()
        sec_a     = self.signup_security_answer.get().strip()

        if not all([fullname, username, password, confirm, sec_q, sec_a]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        success, msg, _ = self.db.register_user(
            username, password, fullname,
            security_question=sec_q,
            security_answer=sec_a.lower()   # store lowercase for case-insensitive matching
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.show_login()
        else:
            messagebox.showerror("Error", msg)

    def handle_forgot_step1(self):
        """Look up the security question for the given username."""
        username = self.forgot_username.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter your username")
            return

        result = self.db.get_security_question(username)
        if result is None:
            messagebox.showerror("Error", "Username not found")
            return

        self.show_forgot_step2(username, result)

    def handle_forgot_step2(self):
        """Verify the security answer and reset the password."""
        username         = self._reset_username
        answer           = self.forgot_answer.get().strip().lower()
        new_password     = self.forgot_new_password.get()
        confirm_password = self.forgot_confirm_password.get()

        if not all([answer, new_password, confirm_password]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if len(new_password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        success, message = self.db.reset_password_with_answer(username, answer, new_password)
        if success:
            messagebox.showinfo("Success", message)
            self.show_login()
        else:
            messagebox.showerror("Error", message)

    def open_dashboard(self):
        self.root.destroy()
        if self.on_login_success is not None:
            self.on_login_success(self.current_user, self.db)
            return
        # Fallback for standalone execution
        from main import launch_dashboard
        launch_dashboard(self.current_user, self.db)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    AuthenticationGUI().run()
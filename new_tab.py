import tkinter as tk
import threading

class NewTabMixin:
    def create_new_tab(self):
        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='Test Tab')
        self.new_label = tk.Label(
            tab,
            text="Loading...",
            font=('Times New Roman', 12),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            anchor='nw',
            justify='left'
        )
        self.new_label.pack(padx=20, pady=20, anchor='nw')
        threading.Thread(target=self.load_new_content, daemon=True).start()

    def load_new_content(self):
        users = self.db_manager.get_all_usernames()   # ← calls the backend, doesn't run SQL itself

        if users:
            text = "Users in Database:\n\n"
            for user in users:
                text += f"Username: {user['username']}, Full Name: {user['full_name']}, Created At: {user['created_at']}\n"
        else:
            text = "No users found or error fetching data."

        self.root.after(0, lambda: self.new_label.config(text=text))
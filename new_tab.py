import sqlite3
import tkinter as tk
import threading 
class NewTabMixin:
    def create_new_tab(self):
        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='Test Tab')
        self.new_label = tk.Label(
            tab,
            text= "The New Tab",
            font=('Times New Romen',12),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            anchor='nw',
            justify='left'
        )
        self.new_label.pack(padx=20,pady=20,anchor='nw')
        threading.Thread(target=self.new__content,daemon=True).start()
    def new_content(self):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT username, full_name, created_at FROM users')
            rows= cursor.fetchall()
            conn.close()
            return [{'username': row[0], 'full_name': row[1], 'created_at': row[2]} for row in rows]
        except Exception as e:
            print(f"Error fetching new content: {e}")
            return []
    def new__content(self):
        content = self.db_manager.new_content()
        if content:
            text = "Users in Database:\n\n"
            for user in content:
                text += f"Username: {user['username']}, Full Name: {user['full_name']}, Created At: {user['created_at']}\n"
            self.new_label.config(text=text)
        else:
            self.new_label.config(text="No users found or error fetching data.")
        self.root.after(5000, lambda: self.new_label.config(text=text))  
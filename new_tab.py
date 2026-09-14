import tkinter as tk
import threading
class NewTabMixin:
    def create_new_tab(self):
        tab = tk.Frame(self.notebook, bg=self.COLORS['bg_dark'])
        self.notebook.add(tab, text='Test Tab')
        self.new_label  = tk.Label(
            tab, bg=self.COLORS['bg_dark'], fg=self.COLORS['text'], font=('Segoe UI', 14, 'bold'), 
            text="This is a test tab."
            )
        self.new_label.pack(pady=20 , padx=20)
        threading.Thread(target=self.update_new_tab, daemon=True).start()
    def update_new_tab(self):
            info = self.hardware.get_all_hardware_info()
            cpu = info['cpu']
            text = (
                     f"Model:            {cpu['model']}\n"
                     f"Physical Cores:   {cpu['physical_cores']}"

            )
            self.root.after(0,lambda: self.new_label.config(text=text))
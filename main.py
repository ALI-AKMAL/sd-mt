import tkinter as tk
from app import SystemMonitorUI
from cleanup_module import CleanupManager
from hardware_info_module import HardwareInfo
from monitor_backend import SystemMonitor
from process_manager import ProcessManager
def launch_dashboard(current_user=None, db_manager=None):
    """Launch the main desktop dashboard after successful authentication. only test"""
    root = tk.Tk()
    monitor = SystemMonitor()
    hardware = HardwareInfo()
    cleanup = CleanupManager()
    process_mgr = ProcessManager()
    SystemMonitorUI(
        root,
        monitor,
        hardware,
        cleanup,
        process_mgr,
        current_user=current_user,
        db_manager=db_manager,
    )
    root.mainloop()
def main():
    from auth_gui import AuthenticationGUI
    auth = AuthenticationGUI(on_login_success=launch_dashboard)
    auth.run()
if __name__ == "__main__":
    main()
import psutil
import os
import platform
from datetime import datetime
class ProcessManager:
    # Critical processes that should show warning before termination
    CRITICAL_PROCESSES = {
        'Windows': [
            'system', 'csrss.exe', 'smss.exe', 'wininit.exe', 'services.exe',
            'lsass.exe', 'winlogon.exe', 'svchost.exe', 'dwm.exe', 'explorer.exe',
            'systemsettings.exe', 'taskmgr.exe', 'registry'
        ]
    }
    def __init__(self):
        """Initialize process manager"""
        self.system = psutil.WINDOWS 
        self.critical_list = self._get_critical_processes()
        
    def _get_critical_processes(self):

        """Get list of critical processes for current OS"""

        system = platform.system()
        
        if system == 'Windows':
            return [p.lower() for p in self.CRITICAL_PROCESSES['Windows']]
        
        else:
            return []
    
    def get_all_processes(self, sort_by='cpu', limit=None):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            try:
                # Get basic info
                pinfo = proc.info
                
                # Get CPU and memory info
                with proc.oneshot():
                    pinfo['cpu_percent'] = proc.cpu_percent(interval=None)
                    pinfo['memory_mb'] = proc.memory_info().rss / (1024 * 1024)
                    pinfo['memory_percent'] = proc.memory_percent()
                    
                    try:
                        pinfo['num_threads'] = proc.num_threads()
                    except:
                        pinfo['num_threads'] = 0
                    
                    try:
                        pinfo['create_time'] = datetime.fromtimestamp(proc.create_time())
                    except:
                        pinfo['create_time'] = None
                
                # Check if critical
                pinfo['is_critical'] = self.is_critical_process(pinfo['name'], pinfo['pid'])
        
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort processes
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
        elif sort_by == 'name':
            processes.sort(key=lambda x: x['name'].lower())
        elif sort_by == 'pid':
            processes.sort(key=lambda x: x['pid'])
        
        # Apply limit
        if limit:
            processes = processes[:limit]
        
        return processes
    
    def get_process_details(self, pid):
        """
        Get detailed information about a specific process
        
        Args:
            pid: Process ID
            
        Returns:
            dict: Detailed process information
        """
        try:
            proc = psutil.Process(pid)
            
            with proc.oneshot():
                details = {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'status': proc.status(),
                    'cpu_percent': proc.cpu_percent(interval=None),
                    'memory_mb': proc.memory_info().rss / (1024 * 1024),
                    'memory_percent': proc.memory_percent(),
                    'num_threads': proc.num_threads(),
                    'username': proc.username(),
                    'create_time': datetime.fromtimestamp(proc.create_time()),
                    'is_critical': self.is_critical_process(proc.name(), pid)
                }
                
                try:
                    details['exe'] = proc.exe()
                except:
                    details['exe'] = 'N/A'
                
                try:
                    details['cwd'] = proc.cwd()
                except:
                    details['cwd'] = 'N/A'
                
                try:
                    details['cmdline'] = ' '.join(proc.cmdline())
                except:
                    details['cmdline'] = 'N/A'
                
                return details
        
        except psutil.NoSuchProcess:
            return None
        except psutil.AccessDenied:
            return {'error': 'Access denied'}
        except Exception as e:
            return {'error': str(e)}
    
    def is_critical_process(self, process_name, pid=None):
        """
        Check if a process is critical to system operation
        
        Args:
            process_name: Name of the process
            pid: Process ID (optional, for additional checks)
            
        Returns:
            bool: True if critical
        """
        if not process_name:
            return False
        
        # Check against known critical processes
        name_lower = process_name.lower()
        if any(crit in name_lower for crit in self.critical_list):
            return True
        
        # Check PID (very low PIDs are usually system processes)
        if pid and pid < 100:
            return True
        
        # Check if it's a system process (Windows)
        if process_name.lower() in ['system', 'registry']:
            return True
        
        return False
    
    def terminate_process(self, pid, force=False):
        """
        Terminate a process
        
        Args:
            pid: Process ID to terminate
            force: If True, use kill instead of terminate
            
        Returns:
            dict: Result with success status and message
        """
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            # Check if critical
            is_critical = self.is_critical_process(proc_name, pid)
            
            # Terminate or kill
            if force:
                proc.kill()
                action = 'killed'
            else:
                proc.terminate()
                action = 'terminated'
            
            return {
                'success': True,
                'pid': pid,
                'name': proc_name,
                'action': action,
                'was_critical': is_critical,
                'message': f'Process {proc_name} (PID: {pid}) {action} successfully'
            }
        except psutil.NoSuchProcess:
            return {
                'success': False,
                'pid': pid,
                'error': 'Process not found',
                'message': f'Process with PID {pid} does not exist'
            }
        except psutil.AccessDenied:
            return {
                'success': False,
                'pid': pid,
                'error': 'Access denied',
                'message': f'Access denied. Try running as administrator/root'
            }
        except Exception as e:
            return {
                'success': False,
                'pid': pid,
                'error': str(e),
                'message': f'Failed to terminate process: {str(e)}'
            }
    
    def get_process_tree(self, pid):
        """
        Get process tree (parent and children)
        
        Args:
            pid: Process ID
            
        Returns:
            dict: Process tree information
        """
        try:
            proc = psutil.Process(pid)
            
            tree = {
                'process': {
                    'pid': proc.pid,
                    'name': proc.name()
                },
                'parent': None,
                'children': []
            }
            
            # Get parent
            try:
                parent = proc.parent()
                if parent:
                    tree['parent'] = {
                        'pid': parent.pid,
                        'name': parent.name()
                    }
            except:
                pass
            # Get children
            try:
                children = proc.children(recursive=False)
                for child in children:
                    tree['children'].append({
                        'pid': child.pid,
                        'name': child.name()
                    })
            except:
                pass
            
            return tree
        
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_summary(self):
        """Get summary of system processes"""
        try:
            processes = list(psutil.process_iter(['pid', 'name']))
            
            total_processes = len(processes)
            running = sum(1 for p in psutil.process_iter(['status']) if p.info['status'] == 'running')
            sleeping = sum(1 for p in psutil.process_iter(['status']) if p.info['status'] == 'sleeping')
            
            return {
                'total': total_processes,
                'running': running,
                'sleeping': sleeping,
                'stopped': total_processes - running - sleeping
            }
        
        except Exception as e:
            return {
                'total': 0,
                'running': 0,
                'sleeping': 0,
                'stopped': 0,
                'error': str(e)
            }
    
    def search_processes(self, query):
        """
        Search for processes by name
        
        Args:
            query: Search query
            
        Returns:
            list: Matching processes
        """
        query_lower = query.lower()
        matching = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                if query_lower in proc.info['name'].lower():
                    pinfo = proc.info
                    pinfo['memory_mb'] = proc.memory_info().rss / (1024 * 1024)
                    pinfo['is_critical'] = self.is_critical_process(pinfo['name'], pinfo['pid'])
                    matching.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return matching
def main():
    """Test process manager"""
    print("=" * 80)
    print("Process Manager Test")
    print("=" * 80)
    print()
    pm = ProcessManager()
    # System summary
    print("System Summary:")
    summary = pm.get_system_summary()
    print(f"  Total Processes: {summary['total']}")
    print(f"  Running: {summary['running']}")
    print(f"  Sleeping: {summary['sleeping']}")
    print()
    # Top 10 CPU-consuming processes
    print("Top 10 Processes by CPU:")
    processes = pm.get_all_processes(sort_by='cpu', limit=10)
    print(f"{'PID':<8} {'Name':<30} {'CPU%':<10} {'Memory (MB)':<12} {'Critical'}")
    print("-" * 80)
    for proc in processes:
        critical_mark = "⚠️ YES" if proc['is_critical'] else "   No"
        print(f"{proc['pid']:<8} {proc['name']:<30} {proc['cpu_percent']:<10.2f} "
              f"{proc['memory_mb']:<12.2f} {critical_mark}")
    print("\n" + "=" * 80)
    print("NOTE: Critical processes show ⚠️ warning before termination")
    print("=" * 80)
if __name__ == "__main__":
    main()
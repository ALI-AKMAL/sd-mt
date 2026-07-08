import os
import shutil
import platform
import subprocess
from pathlib import Path
class CleanupManager:
    def __init__(self):
        """Initialize cleanup manager"""
        self.system = platform.system()
        self.temp_locations = self._get_temp_locations()
    def _get_temp_locations(self):
        """Get temporary file locations based on OS"""
        locations = {
            'Windows Temp': [],
            'User Temp': [],
            'Browser Cache': [],
            'System Cache': [],
            'Recycle Bin': []
        }
        if self.system == 'Windows':
            # Windows temp locations
            locations['Windows Temp'] = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                'C:\\Windows\\Temp'
            ]
            locations['User Temp'] = [
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp')
            ]
            locations['Browser Cache'] = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
                os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles')
            ]
            locations['Recycle Bin'] = [
                'C:\\$Recycle.Bin'
            ]
        elif self.system == 'Linux':
            # Linux temp locations
            locations['System Temp'] = [
                '/tmp',
                '/var/tmp'
            ]
            locations['User Cache'] = [
                os.path.join(os.path.expanduser('~'), '.cache')
            ]
        elif self.system == 'Darwin':  # macOS
            # macOS temp locations
            locations['System Temp'] = [
                '/tmp',
                '/var/tmp'
            ]
            locations['User Cache'] = [
                os.path.join(os.path.expanduser('~'), 'Library', 'Caches')
            ]
        return locations
    def scan_temp_files(self, category=None):
        """
        Scan for temporary files
        Args:
            category: Specific category to scan (None = all)   
        Returns:
            dict: Scan results with file count and size
        """
        results = {
            'categories': {},
            'total_files': 0,
            'total_size_bytes': 0,
            'total_size_mb': 0,
            'total_size_gb': 0
        }
        categories_to_scan = [category] if category else self.temp_locations.keys()
        for cat in categories_to_scan:
            if cat not in self.temp_locations:
                continue
            cat_files = 0
            cat_size = 0
            cat_paths = []
            for location in self.temp_locations[cat]:
                if not location or not os.path.exists(location):
                    continue
                
                try:
                    for root, dirs, files in os.walk(location):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                file_size = os.path.getsize(file_path)
                                cat_files += 1
                                cat_size += file_size
                                cat_paths.append(file_path)
                            except (PermissionError, FileNotFoundError):
                                continue
                except (PermissionError, OSError):
                    continue
            results['categories'][cat] = {
                'file_count': cat_files,
                'size_bytes': cat_size,
                'size_mb': round(cat_size / (1024 ** 2), 2),
                'size_gb': round(cat_size / (1024 ** 3), 2),
                'paths': cat_paths[:100]  # Limit to 100 paths for display
            }
            results['total_files'] += cat_files
            results['total_size_bytes'] += cat_size
        results['total_size_mb'] = round(results['total_size_bytes'] / (1024 ** 2), 2)
        results['total_size_gb'] = round(results['total_size_bytes'] / (1024 ** 3), 2)
        return results
    def open_file_explorer(self, path=None):
        """
        Open file explorer at specified path
        Args:
            path: Path to open (None = user home directory)
        Returns:
            bool: True if successful
        """
        if path is None:
            path = os.path.expanduser('~')
        try:
            if self.system == 'Windows':
                os.startfile(path)
            elif self.system == 'Darwin':  # macOS
                subprocess.Popen(['open', path])
            else:  # Linux
                subprocess.Popen(['xdg-open', path])
            return True
        except Exception as e:
            print(f"Error opening file explorer: {e}")
            return False
    def open_temp_folder(self):
        """Open system temp folder in file explorer"""
        if self.system == 'Windows':
            temp_path = os.environ.get('TEMP', 'C:\\Windows\\Temp')
        else:
            temp_path = '/tmp'
        return self.open_file_explorer(temp_path)
    def clean_category(self, category):
        """
        Clean files in a specific category
        Args:
            category: Category to clean
        Returns:
            dict: Results with files deleted and space freed
        """
        if category not in self.temp_locations:
            return {
                'success': False,
                'files_deleted': 0,
                'space_freed_bytes': 0,
                'space_freed_mb': 0,
                'errors': ['Invalid category']
            }
        files_deleted = 0
        space_freed = 0
        errors = []
        for location in self.temp_locations[category]:
            if not location or not os.path.exists(location):
                continue
            try:
                for root, dirs, files in os.walk(location):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            files_deleted += 1
                            space_freed += file_size
                        except (PermissionError, FileNotFoundError, OSError) as e:
                            errors.append(f"Could not delete {file}: {str(e)}")
                            continue
            except (PermissionError, OSError) as e:
                errors.append(f"Could not access {location}: {str(e)}")
                continue
        return {
            'success': True,
            'files_deleted': files_deleted,
            'space_freed_bytes': space_freed,
            'space_freed_mb': round(space_freed / (1024 ** 2), 2),
            'space_freed_gb': round(space_freed / (1024 ** 3), 2),
            'errors': errors[:10]  # Limit errors to first 10
        }
    def get_disk_space(self):
        """Get current disk space information"""
        try:
            if self.system == 'Windows':
                drive = 'C:\\'
            else:
                drive = '/'
            total, used, free = shutil.disk_usage(drive)
            return {
                'total_gb': round(total / (1024 ** 3), 2),
                'used_gb': round(used / (1024 ** 3), 2),
                'free_gb': round(free / (1024 ** 3), 2),
                'used_percent': round((used / total) * 100, 1)
            }
        except Exception as e:
            print(f"Error getting disk space: {e}")
            return None
    def get_large_files(self, path=None, min_size_mb=100, limit=20):
        """
        Find large files on the system
        Args:
            path: Path to search (None = user home)
            min_size_mb: Minimum file size in MB
            limit: Maximum number of files to return
        Returns:
            list: List of large files with details
        """
        if path is None:
            path = os.path.expanduser('~')
        large_files = []
        min_size_bytes = min_size_mb * 1024 * 1024
        try:
            for root, dirs, files in os.walk(path):
                # Skip system directories
                dirs[:] = [d for d in dirs if d not in [
                    'AppData', 'Application Data', '.git', 'node_modules',
                    'Library', 'System', 'Windows'
                ]]
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        if file_size >= min_size_bytes:
                            large_files.append({
                                'path': file_path,
                                'name': file,
                                'size_bytes': file_size,
                                'size_mb': round(file_size / (1024 ** 2), 2),
                                'size_gb': round(file_size / (1024 ** 3), 2)
                            })
                            if len(large_files) >= limit:
                                break
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
                if len(large_files) >= limit:
                    break
        except Exception as e:
            print(f"Error finding large files: {e}")
        # Sort by size (largest first)
        large_files.sort(key=lambda x: x['size_bytes'], reverse=True)
        return large_files[:limit]
def main():
    """Test cleanup functionality"""
    print("=" * 70)
    print("Cleanup Module Test")
    print("=" * 70)
    print()
    cleanup = CleanupManager()
    # Show disk space
    print("Current Disk Space:")
    disk = cleanup.get_disk_space()
    if disk:
        print(f"  Total: {disk['total_gb']} GB")
        print(f"  Used: {disk['used_gb']} GB ({disk['used_percent']}%)")
        print(f"  Free: {disk['free_gb']} GB")
    print()
    # Scan temp files
    print("Scanning temporary files...")
    results = cleanup.scan_temp_files()
    print(f"\nTotal Files Found: {results['total_files']}")
    print(f"Total Size: {results['total_size_mb']} MB ({results['total_size_gb']} GB)")
    print()
    print("By Category:")
    for cat, data in results['categories'].items():
        if data['file_count'] > 0:
            print(f"  {cat}: {data['file_count']} files, {data['size_mb']} MB")
    print("\n" + "=" * 70)
    print("NOTE: Run with admin/sudo privileges for full access")
    print("=" * 70)
if __name__ == "__main__":
    main()
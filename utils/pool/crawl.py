import requests
import json
import yaml
import time
from yaml.loader import SafeLoader

def get_file_list():
    """Fetch the list of files and directories from the GitHub repository."""
    try:
        start = time.time()
        response = requests.get('https://api.github.com/repos/changfengoss/pub/git/trees/main?recursive=1', headers={'Cache-Control': 'no-cache'})
        if response.status_code == 200:
            rawdata = response.json()
            data = rawdata['tree']
            dirlist = [item['path'] for item in data]
            end = time.time()
            print(f"Fetch changfengoss/pub succeeded in {end - start:.2f} seconds")
            return dirlist, len(dirlist)
        else:
            print(f"Failed to fetch file list, status code: {response.status_code}")
            return [], 0
    except Exception as e:
        print(f"Error fetching file list: {e}")
        return [], 0

def get_latest_yaml_file(dirlist):
    """Find the latest YAML file based on the directory structure."""
    try:
        # Filter directories that are date directories
        date_dirs = [path for path in dirlist if path.startswith('data/') and path.count('/') == 2]
        
        # Sort date directories by date
        sorted_date_dirs = sorted(date_dirs, key=lambda x: x.split('/')[1], reverse=True)
        latest_date_dir = sorted_date_dirs[0] if sorted_date_dirs else None
        
        if latest_date_dir:
            # Filter YAML files in the latest date directory
            date_files = [path for path in dirlist if path.startswith(latest_date_dir) and path.endswith('.yaml')]
            
            # Sort YAML files by file name (if needed, can add more sorting logic)
            sorted_files = sorted(date_files, reverse=True)
            latest_file = sorted_files[0] if sorted_files else None
            
            latest_date = latest_date_dir.split('/')[1] if latest_date_dir else None
            latest_filename = latest_file.split('/')[2] if latest_file else None
            
            return latest_date, latest_filename
        else:
            print("No date directories found.")
            return None, None
    except Exception as e:
        print(f"Error finding the latest YAML file: {e}")
        return None, None

# Example usage of the modified functions
if __name__ == "__main__":
    directories, total_files = get_file_list()
    if total_files > 0:
        latest_date, latest_file = get_latest_yaml_file(directories)
        if latest_date and latest_file:
            print(f"Latest YAML file found: {latest_date}/{latest_file}")
        else:
            print("No valid YAML files found.")
    else:
        print("No files or directories found.")

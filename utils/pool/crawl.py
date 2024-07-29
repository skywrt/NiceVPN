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
        date_dirs = sorted([path for path in dirlist if path.startswith('data/') and path.count('/') == 2])
        latest_date_dir = date_dirs[-1] if date_dirs else None

        if latest_date_dir:
            # Filter YAML files in the latest date directory
            date_files = sorted([path for path in dirlist if path.startswith(latest_date_dir) and path.endswith('.yaml')])
            latest_file = date_files[-1] if date_files else None
            return latest_date_dir.split('/')[1], latest_file.split('/')[2] if latest_file else None
        else:
            print("No date directories found.")
            return None, None
    except Exception as e:
        print(f"Error finding the latest YAML file: {e}")
        return None, None

# Removing the get_proxies function, as it is no longer needed

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

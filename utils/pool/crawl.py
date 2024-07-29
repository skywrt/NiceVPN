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
            return dirlist
        else:
            print(f"Failed to fetch file list, status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching file list: {e}")
        return []

def get_latest_yaml_file(dirlist):
    """Find the latest YAML file based on the directory structure."""
    try:
        # Extract date directories
        date_dirs = [path for path in dirlist if path.startswith('data/') and path.count('/') == 2]
        
        if not date_dirs:
            print("No date directories found.")
            return None, None
        
        # Sort date directories by date
        sorted_date_dirs = sorted(date_dirs, key=lambda x: x.split('/')[1], reverse=True)
        latest_date_dir = sorted_date_dirs[0]
        
        # Extract YAML files from the latest date directory
        date_files = [path for path in dirlist if path.startswith(latest_date_dir) and path.endswith('.yaml')]
        
        if not date_files:
            print(f"No YAML files found in directory: {latest_date_dir}")
            return None, None
        
        # Sort files to get the latest one (if filenames need to be sorted)
        latest_file = max(date_files, key=lambda x: x.split('/')[-1])
        
        latest_date = latest_date_dir.split('/')[1]
        latest_filename = latest_file.split('/')[-1]
        
        return latest_date, latest_filename
    except Exception as e:
        print(f"Error finding the latest YAML file: {e}")
        return None, None

# Example usage of the modified functions
if __name__ == "__main__":
    directories = get_file_list()
    if directories:
        latest_date, latest_file = get_latest_yaml_file(directories)
        if latest_date and latest_file:
            print(f"Latest YAML file found: {latest_date}/{latest_file}")
        else:
            print("No valid YAML files found.")
    else:
        print("No files or directories found.")

import requests
import json
import time

def get_file_list():
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
    # Find the latest date directory
    date_dirs = sorted([path for path in dirlist if path.startswith('data/') and path.count('/') == 2])
    latest_date_dir = date_dirs[-1] if date_dirs else None
    
    if latest_date_dir:
        # Get all files in the latest date directory
        date_files = sorted([path for path in dirlist if path.startswith(latest_date_dir) and path.endswith('.yaml')])
        latest_file = date_files[-1] if date_files else None
        return latest_date_dir.split('/')[1], latest_file.split('/')[2] if latest_file else None
    else:
        return None, None

# Main execution
dirlist, count = get_file_list()
print(f"Total files and directories: {count}")

if count > 0:
    latest_date, latest_file = get_latest_yaml_file(dirlist)
    if latest_date and latest_file:
        print(f"Latest file found: {latest_date}/{latest_file}")
    else:
        print("No valid YAML files found in the latest date directory.")
else:
    print("No files or directories found in the repository.")

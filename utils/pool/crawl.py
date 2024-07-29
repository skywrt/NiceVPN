import requests
import yaml
from datetime import datetime

def get_latest_date_and_file():
    base_url = 'https://api.github.com/repos/changfengoss/pub/git/trees/main?recursive=1'
    response = requests.get(base_url)
    
    if response.status_code != 200:
        print(f"Failed to fetch data from GitHub: {response.status_code}")
        return None, None

    data = response.json()
    tree = data.get('tree', [])
    
    # Extract directories with date format YYYY_MM_DD
    date_dirs = set()
    for item in tree:
        if 'path' in item:
            path = item['path']
            parts = path.split('/')
            if len(parts) > 1 and parts[1].count('_') == 2:
                date_dirs.add(parts[1])
    
    if not date_dirs:
        print("No valid date directories found.")
        return None, None

    # Find the latest date
    latest_date = max(date_dirs)
    latest_file = None
    
    # Find the latest file in the latest date directory
    for item in tree:
        if 'path' in item:
            path_str = item['path']
            if path_str.startswith(f'data/{latest_date}/'):
                latest_file = path_str.split('/')[-1]
                break
    
    if not latest_file:
        print("No files found for the latest date.")
        return latest_date, None
    
    return latest_date, latest_file

def fetch_yaml_file(date, filename):
    url = f'https://raw.githubusercontent.com/changfengoss/pub/main/data/{date}/{filename}'
    try:
        response = requests.get(url, timeout=240)
        response.raise_for_status()
        return yaml.safe_load(response.text)
    except requests.RequestException as e:
        print(f"Error fetching YAML file {url}: {e}")
        return None

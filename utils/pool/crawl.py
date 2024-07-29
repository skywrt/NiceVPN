import requests
import yaml
import json

# Define the base URL for accessing GitHub raw content
BASE_URL = 'https://raw.githubusercontent.com/changfengoss/pub/main/data/'

def get_latest_date():
    """
    Get the latest date directory from the repository.
    Returns:
        str: The latest date directory in YYYY_MM_DD format.
    """
    try:
        response = requests.get('https://api.github.com/repos/changfengoss/pub/git/trees/main?recursive=1')
        response.raise_for_status()
        
        # Extract all paths and filter for date directories
        paths = [item['path'] for item in response.json().get('tree', [])]
        date_dirs = {path.split('/')[1] for path in paths if len(path.split('/')) == 2 and path.split('/')[1].count('_') == 2}
        latest_date = max(date_dirs, default=None)
        
        return latest_date
    
    except requests.RequestException as e:
        print(f"Error fetching latest date: {e}")
        return None

def get_latest_file(date):
    """
    Get the latest YAML file from the latest date directory.
    Args:
        date (str): The latest date directory in YYYY_MM_DD format.
    Returns:
        str: The name of the latest YAML file.
    """
    try:
        response = requests.get(f'https://api.github.com/repos/changfengoss/pub/git/trees/main/0pmtpm/{date}?recursive=1')
        response.raise_for_status()
        
        # Extract all file paths and filter for YAML files
        paths = [item['path'] for item in response.json().get('tree', []) if item['path'].endswith('.yaml')]
        latest_file = max(paths, default=None, key=lambda p: p.split('/')[-1])
        
        return latest_file
    
    except requests.RequestException as e:
        print(f"Error fetching latest file for date {date}: {e}")
        return None

def fetch_yaml_file(date, file_name):
    """
    Fetch the YAML file content from the repository.
    Args:
        date (str): The date directory in YYYY_MM_DD format.
        file_name (str): The name of the YAML file to fetch.
    Returns:
        dict: The content of the YAML file.
    """
    try:
        url = f'{BASE_URL}{date}/{file_name}'
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse YAML content
        return yaml.safe_load(response.text)
    
    except requests.RequestException as e:
        print(f"Error fetching YAML file {file_name}: {e}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_name}: {e}")
        return None

if __name__ == '__main__':
    latest_date = get_latest_date()
    
    if latest_date:
        latest_file = get_latest_file(latest_date)
        
        if latest_file:
            yaml_content = fetch_yaml_file(latest_date, latest_file)
            if yaml_content:
                print("Successfully fetched and parsed YAML file.")
                print(yaml_content)
            else:
                print("Failed to fetch or parse the YAML file.")
        else:
            print("No YAML file found for the latest date.")
    else:
        print("Failed to determine the latest date.")

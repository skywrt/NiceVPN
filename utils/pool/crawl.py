import requests
import yaml

# Define the base URL for accessing GitHub raw content
BASE_URL = 'https://raw.githubusercontent.com/changfengoss/pub/main/data/'

def get_latest_date_and_file():
    """
    Get the latest date and the latest YAML file for that date.
    
    Returns:
        tuple: (latest_date, latest_file)
            - latest_date (str): The latest date directory in YYYY_MM_DD format.
            - latest_file (str): The name of the latest YAML file in the date directory.
    """
    try:
        # Fetch the list of files and directories from the main repository
        response = requests.get('https://api.github.com/repos/changfengoss/pub/git/trees/main?recursive=1')
        response.raise_for_status()
        tree = response.json().get('tree', [])
        
        # Extract all date directories (format YYYY_MM_DD)
        date_dirs = {path.split('/')[1] for path in tree if len(path.split('/')) == 2 and path.split('/')[1].count('_') == 2}
        latest_date = max(date_dirs, default=None)
        
        if not latest_date:
            return None, None
        
        # Fetch files in the latest date directory
        response = requests.get(f'https://api.github.com/repos/changfengoss/pub/git/trees/main/0pmtpm/{latest_date}?recursive=1')
        response.raise_for_status()
        tree = response.json().get('tree', [])
        
        # Extract all YAML files and find the latest one
        yaml_files = [item['path'] for item in tree if item['path'].endswith('.yaml')]
        latest_file = max(yaml_files, default=None, key=lambda p: p.split('/')[-1])
        
        return latest_date, latest_file
    
    except requests.RequestException as e:
        print(f"Error fetching latest date or file: {e}")
        return None, None

def fetch_yaml_file(date, file_name):
    """
    Fetch the YAML file content from the repository.
    Args:
        date (str): The date directory in YYYY_MM_DD format.
        file_name (str): The name of the YAML file to fetch.
    Returns:
        dict: The content of the YAML file or None if there was an error.
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

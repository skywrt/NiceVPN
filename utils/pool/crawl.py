import requests
import json
import yaml
import time
from datetime import datetime

def get_file_list():
    """
    Fetch the list of all files and directories from the GitHub repository.
    Returns:
        list: A list of all file paths.
        int: Total number of files and directories.
    """
    try:
        start = time.time()
        response = requests.get('https://api.github.com/repos/changfengoss/pub/git/trees/main?recursive=1')
        response.raise_for_status()  # Ensure we notice bad responses
        rawdata = response.json()
        data = rawdata.get('tree', [])
        dirlist = [item['path'] for item in data]
        end = time.time()
        print(f"Fetch changfengoss/pub succeeded in {end - start:.2f} seconds")
        return dirlist, len(dirlist)
    except requests.RequestException as e:
        print(f"Error fetching file list: {e}")
        return [], 0

def get_latest_date():
    """
    Determine the latest available date directory from the file list.
    Returns:
        str: The latest date in 'YYYY_MM_DD' format.
    """
    dirlist, _ = get_file_list()
    dates = [path.split('/')[1] for path in dirlist if len(path.split('/')) > 1 and path.split('/')[1].count('_') == 2]
    
    if not dates:
        print("No date directories found.")
        return None

    latest_date = max(dates, default=None)
    print(f"Latest date directory found: {latest_date}")
    return latest_date

def get_proxies(date, file):
    """
    Fetch proxies from the specified YAML file.
    Args:
        date (str): The date directory to fetch the file from.
        file (str): The YAML file to fetch.
    Returns:
        list: A list of proxies.
    """
    baseurl = 'https://raw.githubusercontent.com/changfengoss/pub/main/data/'
    url = f"{baseurl}{date}/{file}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        working = yaml.safe_load(response.text)
        data_out = [x for x in working.get('proxies', [])]
        return data_out
    except requests.RequestException as e:
        print(f"Error fetching proxies from {url}: {e}")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing YAML from {url}: {e}")
        return []

def get_latest_yaml_file():
    """
    Get the latest YAML file from the latest date.
    Returns:
        str: The path to the latest YAML file.
    """
    latest_date = get_latest_date()
    if not latest_date:
        print("No date directories found.")
        return None

    dirlist, _ = get_file_list()
    yaml_files = [path for path in dirlist if path.startswith(f"data/{latest_date}/") and path.endswith('.yaml')]
    
    if yaml_files:
        latest_yaml = max(yaml_files, key=lambda x: x.split('/')[-1])
        print(f"Latest YAML file found: {latest_yaml}")
        return latest_yaml
    else:
        print("No YAML files found for the latest date.")
        return None

def fetch_latest_proxies():
    """
    Fetch proxies from the latest YAML file.
    Returns:
        list: A list of proxies from the latest YAML file.
    """
    latest_yaml_file = get_latest_yaml_file()
    if not latest_yaml_file:
        return []

    # Extract filename from path
    filename = latest_yaml_file.split('/')[-1]
    latest_date = latest_yaml_file.split('/')[1]
    return get_proxies(latest_date, filename)

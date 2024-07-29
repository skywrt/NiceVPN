import requests
import json
import yaml
import time
from datetime import datetime

def get_file_list():
    """
    Fetch the list of files from the GitHub repository and return directory paths and count.
    Returns:
        tuple: A tuple containing the list of file paths and the total count of files.
    """
    try:
        start = time.time()
        response = requests.get('https://api.github.com/repos/changfengoss/pub/git/trees/main?recursive=1')
        response.raise_for_status()  # Raise an error for bad HTTP responses
        rawdata = response.json()
        data = rawdata['tree']
        dirlist = [x['path'] for x in data if x['path'].endswith('.yaml')]
        count = len(dirlist)
        end = time.time()
        print(f"Fetch changfengoss/pub succeeded in {end-start:.2f} seconds")
        return dirlist, count
    except requests.RequestException as e:
        print(f"Failed to fetch file list: {e}")
        return [], 0

def get_proxies(date, file):
    """
    Fetch proxies from the specified YAML file for a given date.
    Args:
        date (str): Date in 'YYYY_MM_DD' format.
        file (str): YAML file name.
    Returns:
        list: A list of proxies extracted from the YAML file.
    """
    baseurl = f'https://raw.githubusercontent.com/changfengoss/pub/main/data/{date}/'
    url = baseurl + file
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        working = yaml.safe_load(response.text)
        return working.get('proxies', [])
    except requests.RequestException as e:
        print(f"Error fetching file from {url}: {e}")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {url}: {e}")
        return []

def get_latest_file_date():
    """
    Get the latest date available for YAML files.
    Returns:
        str: Latest date in 'YYYY_MM_DD' format.
    """
    current_date = datetime.now().strftime('%Y_%m_%d')
    return current_date

def get_latest_proxies_file(directories):
    """
    Get the latest YAML file based on the directories list.
    Args:
        directories (list): List of file paths from get_file_list.
    Returns:
        str: The latest YAML file name if available, None otherwise.
    """
    date = get_latest_file_date()
    latest_file = None
    for file in directories:
        if file.startswith(f'{date}/') and file.endswith('.yaml'):
            latest_file = file
            break
    return latest_file

def fetch_latest_proxies():
    """
    Fetch proxies from the latest YAML file.
    Returns:
        list: A list of proxies from the latest YAML file if successful, empty list otherwise.
    """
    directories, _ = get_file_list()
    latest_file = get_latest_proxies_file(directories)
    if latest_file:
        date = latest_file.split('/')[0]
        return get_proxies(date, latest_file.split('/')[-1])
    else:
        print("No latest YAML file found.")
        return []

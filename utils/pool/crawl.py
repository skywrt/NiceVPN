import requests
import yaml
import time
from datetime import datetime

def get_current_date():
    """
    Returns the current date in 'YYYYMMDD' format.
    """
    return datetime.now().strftime('%Y%m%d')

def fetch_file(url):
    """
    Fetch the content of a file from the given URL.
    Args:
        url (str): URL of the file to fetch.
    Returns:
        str: Content of the file if successful, None otherwise.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching file from {url}: {e}")
        return None

def get_latest_yaml_file():
    """
    Get the latest YAML file from the URL based on current date.
    Returns:
        str: The URL of the latest YAML file if successful, None otherwise.
    """
    base_url = 'https://nodefree.org/dy/2024/07/'  # Update this base URL if needed
    current_date = get_current_date()
    url = f"{base_url}{current_date}.yaml"
    
    file_content = fetch_file(url)
    if file_content:
        # Save content to a local file for processing if needed
        local_filename = f"{current_date}.yaml"
        with open(local_filename, 'w') as file:
            file.write(file_content)
        print(f"Latest YAML file downloaded: {local_filename}")
        return local_filename
    else:
        print(f"No YAML file found for date {current_date}.")
        return None

def parse_proxies_from_file(filename):
    """
    Parse proxies from the given YAML file.
    Args:
        filename (str): The path to the YAML file.
    Returns:
        list: A list of proxies extracted from the YAML file.
    """
    try:
        with open(filename, 'r') as file:
            working = yaml.safe_load(file)
        return working.get('proxies', [])
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {filename}: {e}")
        return []

def fetch_latest_proxies():
    """
    Fetch proxies from the latest YAML file.
    Returns:
        list: A list of proxies from the latest YAML file if successful, empty list otherwise.
    """
    latest_yaml_file = get_latest_yaml_file()
    if latest_yaml_file:
        return parse_proxies_from_file(latest_yaml_file)
    else:
        return []

# For debugging purposes
if __name__ == '__main__':
    proxies = fetch_latest_proxies()
    print(proxies)

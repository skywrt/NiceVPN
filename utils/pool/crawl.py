import requests
import yaml
from datetime import datetime

def get_latest_proxies():
    """
    Fetch the latest YAML file from the specified URL and return its content.
    Returns:
        list: A list of proxies extracted from the latest YAML file.
    """
    base_url = 'https://raw.githubusercontent.com/changfengoss/pub/main/data/'
    
    # Get today's date in YYYY_MM_DD format
    today_date = datetime.now().strftime('%Y_%m_%d')
    latest_file_url = f'{base_url}{today_date}/'
    
    try:
        # Fetch the list of files from the latest directory
        response = requests.get(latest_file_url)
        response.raise_for_status()
        
        file_list = response.text.splitlines()  # Assuming each file is listed in a new line
        latest_yaml_file = None
        
        # Find the latest YAML file
        for file_name in file_list:
            if file_name.endswith('.yaml'):
                latest_yaml_file = file_name
                break
        
        if not latest_yaml_file:
            print("No YAML file found in the latest directory.")
            return []

        # Fetch the latest YAML file content
        file_url = f'{latest_file_url}{latest_yaml_file}'
        response = requests.get(file_url)
        response.raise_for_status()
        
        # Load and return proxies from the YAML file
        working = yaml.safe_load(response.text)
        return working.get('proxies', [])
        
    except requests.RequestException as e:
        print(f"Error fetching file: {e}")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return []

# Example usage:
if __name__ == '__main__':
    proxies = get_latest_proxies()
    print("Proxies:", proxies)

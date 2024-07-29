import time
import yaml
import requests
from multiprocessing import Process, Manager
from yaml.loader import SafeLoader
from crawl import get_latest_yaml_file  # Import the function from crawl.py
from parse import parse, makeclash
from clash import push

headers = {'Accept': '*/*', 'Accept-Encoding': 'gzip', 'Connection': 'Keep-Alive', 'User-Agent': 'Clash'}

def local(proxy_list, file):
    try:
        with open(file, 'r') as reader:
            working = yaml.safe_load(reader)
        data_out = []
        for x in working['proxies']:
            data_out.append(x)
        proxy_list.append(data_out)
    except Exception as e:
        print(f"{file}: No such file or error occurred - {e}")

def url(proxy_list, link):
    try:
        response = requests.get(url=link, timeout=240, headers=headers)
        response.raise_for_status()
        yaml_content = yaml.safe_load(response.text)
        
        print(f"Content fetched from {link}: {yaml_content}")  # Debug info
        print(f"Type of fetched content: {type(yaml_content)}")  # Debug info
        
        if isinstance(yaml_content, dict):
            proxies = yaml_content.get('proxies', [])
            if proxies:
                proxy_list.append(proxies)
                print(f"Proxies added from {link}: {proxies}")  # Debug info
            else:
                print("No proxies found in the YAML file.")
        else:
            print(f"Unexpected content format from {link}. Expected a dictionary but got {type(yaml_content)}")
    
    except requests.RequestException as e:
        print(f"Error in Collecting {link}: {e}")
    except yaml.YAMLError as e:
        print(f"YAML Error for {link}: {e}")

def fetch(proxy_list):
    """Fetch the YAML file content and append proxies to the list"""
    latest_yaml_url = get_latest_yaml_file()
    print(f"Latest YAML URL fetched: {latest_yaml_url}")  # Debug info
    if latest_yaml_url:
        try:
            response = requests.get(latest_yaml_url)
            response.raise_for_status()
            yaml_content = yaml.safe_load(response.text)
            proxies = yaml_content.get('proxies', [])
            if proxies:
                proxy_list.append(proxies)
                print(f"Proxies added from {latest_yaml_url}: {proxies}")  # Debug info
            else:
                print("No proxies found in the YAML file.")
        except Exception as e:
            print(f"Error fetching YAML file: {e}")
    else:
        print("No URL found for the latest YAML file.")

if __name__ == '__main__':
    with Manager() as manager:
        proxy_list = manager.list()
        start = time.time()  # Time start

        config = 'config.yaml'
        with open(config, 'r') as reader:
            config = yaml.load(reader, Loader=SafeLoader)
            subscribe_links = config['sub']
            subscribe_files = config['local']
        
        try:
            sfiles = len(subscribe_links)
            tfiles = len(subscribe_links) + len(subscribe_files)
            processes = []

            # Process local files
            for i in subscribe_files:
                p = Process(target=local, args=(proxy_list, i))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()

            # Process URLs
            for i in subscribe_links:
                p = Process(target=url, args=(proxy_list, i))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()

            # Process latest YAML file
            p = Process(target=fetch, args=(proxy_list,))
            p.start()
            processes.append(p)
            for p in processes:
                p.join()
            
            end = time.time()  # Time end
            print("Collecting in " + "{:.2f}".format(end-start) + " seconds")
        
        except Exception as e:
            print(f"Error: {e}")
            end = time.time()  # Time end
            print("Collecting in " + "{:.2f}".format(end-start) + " seconds")

        proxy_list = list(proxy_list)
        proxies = makeclash(proxy_list)
        push(proxies)

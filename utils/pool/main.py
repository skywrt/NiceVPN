import time
import yaml
import requests
from multiprocessing import Process, Manager
from yaml.loader import SafeLoader
from crawl import get_latest_yaml_file
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
    except:
        print(file + ": No such file")

def url(proxy_list, link):
    try:
        working = yaml.safe_load(requests.get(url=link, timeout=240, headers=headers).text)
        data_out = []
        for x in working['proxies']:
            data_out.append(x)
        proxy_list.append(data_out)
    except requests.RequestException as e:
        print(f"Error in Collecting {link}: {e}")

from crawl import get_latest_yaml_file  # Import the function from crawl.py

def fetch(proxy_list, filename):
    """Fetch the YAML file content and append proxies to the list"""
    latest_yaml_url = get_latest_yaml_file()
    if latest_yaml_url:
        try:
            response = requests.get(latest_yaml_url)
            response.raise_for_status()
            yaml_content = yaml.safe_load(response.text)
            proxy_list.append(yaml_content.get('proxies', []))
        except Exception as e:
            print(f"Error fetching YAML file: {e}")
    else:
        print("No URL found for the latest YAML file.")

if __name__ == '__main__':
    with Manager() as manager:
        proxy_list = manager.list()
        start = time.time()  # Time start
        
        # Get the latest date and file name
        latest_date, latest_file = get_latest_date_and_file()
        if not latest_date or not latest_file:
            print("Could not determine the latest file.")
            exit(1)

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
            p = Process(target=fetch, args=(proxy_list, latest_file))
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

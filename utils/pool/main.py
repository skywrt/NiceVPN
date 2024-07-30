import time
import yaml
import requests
from crawl import get_latest_yaml_file
from parse import parse, makeclash
from clash import push
from multiprocessing import Process, Manager
from yaml.loader import SafeLoader

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
        print(file + ": No such file or error occurred -", e)

def url(proxy_list, link):
    try:
        working = yaml.safe_load(requests.get(url=link, timeout=240, headers=headers).text)
        data_out = []
        for x in working['proxies']:
            data_out.append(x)
        proxy_list.append(data_out)
    except Exception as e:
        print("Error in Collecting " + link + ":", e)

def fetch(proxy_list, url):
    try:
        response = requests.get(url, timeout=240, headers=headers)
        response.raise_for_status()
        yaml_content = yaml.safe_load(response.text)
        if isinstance(yaml_content, dict) and 'proxies' in yaml_content:
            proxy_list.append(yaml_content['proxies'])
            print(f"Proxies added from {url}: {yaml_content['proxies']}")
        else:
            print(f"Unexpected content format from {url}. Expected a dictionary with 'proxies'.")
    except requests.RequestException as e:
        print(f"Error fetching YAML file from {url}: {e}")
    except yaml.YAMLError as e:
        print(f"YAML Error for {url}: {e}")

if __name__ == '__main__':
    with Manager() as manager:
        proxy_list = manager.list()
        start = time.time()  # Time start

        config = 'config.yaml'
        with open(config, 'r') as reader:
            config = yaml.load(reader, Loader=SafeLoader)
            subscribe_links = config['sub']
            subscribe_files = config['local']

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
        latest_yaml_url = get_latest_yaml_file()
        if latest_yaml_url:
            p = Process(target=fetch, args=(proxy_list, latest_yaml_url))
            p.start()
            processes.append(p)
            for p in processes:
                p.join()

        end = time.time()  # Time end
        print("Collecting in " + "{:.2f}".format(end-start) + " seconds")

        proxy_list = list(proxy_list)
        proxies = makeclash(proxy_list)
        push(proxies)

import time
import yaml
import requests  # Ensure requests is imported here
from crawl import get_file_list
from parse import parse, makeclash
from clash import push
from multiprocessing import Process, Manager
from yaml.loader import SafeLoader

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip',
    'Connection': 'Keep-Alive',
    'User-Agent': 'Clash'
}

def local(proxy_list, file):
    """Load proxies from a local YAML file."""
    try:
        with open(file, 'r') as reader:
            working = yaml.safe_load(reader)
        data_out = [x for x in working.get('proxies', [])]
        proxy_list.extend(data_out)
    except FileNotFoundError:
        print(f"{file}: No such file")
    except yaml.YAMLError as e:
        print(f"Error reading {file}: {e}")

def url(proxy_list, link):
    """Load proxies from a URL."""
    try:
        response = requests.get(url=link, timeout=240, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        working = yaml.safe_load(response.text)
        data_out = [x for x in working.get('proxies', [])]
        proxy_list.extend(data_out)
    except requests.RequestException as e:
        print(f"Error fetching {link}: {e}")
    except yaml.YAMLError as e:
        print(f"Error parsing {link}: {e}")

def fetch(proxy_list, filename):
    """Fetch proxies from a file in GitHub repository."""
    current_date = time.strftime("%Y_%m_%d", time.localtime())
    baseurl = 'https://raw.githubusercontent.com/changfengoss/pub/main/data/'
    try:
        response = requests.get(url=baseurl + current_date + '/' + filename, timeout=240)
        response.raise_for_status()  # Check if the request was successful
        working = yaml.safe_load(response.text)
        data_out = [x for x in working.get('proxies', [])]
        proxy_list.extend(data_out)
    except requests.RequestException as e:
        print(f"Error fetching {baseurl + current_date + '/' + filename}: {e}")
    except yaml.YAMLError as e:
        print(f"Error parsing {baseurl + current_date + '/' + filename}: {e}")

if __name__ == '__main__':
    with Manager() as manager:
        proxy_list = manager.list()
        current_date = time.strftime("%Y_%m_%d", time.localtime())
        start = time.time()

        config_file = 'config.yaml'
        try:
            with open(config_file, 'r') as reader:
                config = yaml.load(reader, Loader=SafeLoader)
                subscribe_links = config.get('sub', [])
                subscribe_files = config.get('local', [])
        except FileNotFoundError:
            print(f"{config_file}: No such file")
            exit(1)
        except yaml.YAMLError as e:
            print(f"Error reading {config_file}: {e}")
            exit(1)

        directories, total_files = get_file_list()
        data = parse(directories)
        
        sfiles = len(subscribe_links)
        filenames = data.get(current_date, [])
        tfiles = sfiles + len(filenames)

        processes = []

        # Start processes for local files
        for file in subscribe_files:
            p = Process(target=local, args=(proxy_list, file))
            p.start()
            processes.append(p)

        # Start processes for subscribe links
        for link in subscribe_links:
            p = Process(target=url, args=(proxy_list, link))
            p.start()
            processes.append(p)

        # Start processes for GitHub files
        for filename in filenames:
            p = Process(target=fetch, args=(proxy_list, filename))
            p.start()
            processes.append(p)

        # Wait for all processes to complete
        for p in processes:
            p.join()

        end = time.time()
        print(f"Collecting in {end - start:.2f} seconds")

        # Convert multiprocessing list to regular list
        proxy_list = list(proxy_list)
        proxies = makeclash(proxy_list)
        push(proxies)

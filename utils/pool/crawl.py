import requests
from datetime import datetime

REPO = 'changfengoss/pub'
DATA_DIR = 'data'
GITHUB_API_URL = f'https://api.github.com/repos/{REPO}/contents/{DATA_DIR}'

def get_latest_yaml_file():
    """获取最新 YAML 文件的 URL"""
    try:
        # 请求 data 目录的 GitHub API
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()
        
        # 过滤并查找符合日期格式的日期文件夹
        date_folders = []
        for file in files:
            if file['type'] == 'dir':
                try:
                    folder_date = datetime.strptime(file['name'], '%Y_%m_%d')
                    date_folders.append({'name': file['name'], 'url': file['url']})
                except ValueError:
                    # 如果文件夹名不符合日期格式，忽略它
                    print(f"Ignored non-date folder: {file['name']}")
        
        if not date_folders:
            print("No date folders found.")
            return None
        
        # 找到最新的日期文件夹
        latest_date_folder = max(date_folders, key=lambda d: datetime.strptime(d['name'], '%Y_%m_%d'))
        latest_folder_url = latest_date_folder['url']
        print(f"Latest date folder: {latest_date_folder['name']}")
        
        # 请求最新日期文件夹的 GitHub API
        response = requests.get(latest_folder_url)
        response.raise_for_status()
        files = response.json()
        
        # 查找 YAML 文件
        yaml_files = [file for file in files if file['name'].endswith('.yaml')]
        if not yaml_files:
            print("No YAML files found in the latest date folder.")
            return None
        
        # 选择最新的 YAML 文件
        latest_yaml_file = max(yaml_files, key=lambda f: f['name'])  # Use filename if there's no timestamp
        latest_yaml_url = latest_yaml_file['download_url']
        print(f"Latest YAML file URL: {latest_yaml_url}")
        return latest_yaml_url

    except requests.RequestException as e:
        print(f"Error fetching latest YAML file: {e}")
        return None

import requests
from datetime import datetime
import re

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
        
        # 打印 API 返回的内容以便调试
        print("API response for data directory:")
        print(files)
        
        # 查找日期文件夹
        date_folders = [f['name'] for f in files if f['type'] == 'dir' and re.match(r'\d{4}_\d{2}_\d{2}', f['name'])]
        
        if not date_folders:
            print("No date folders found.")
            return None
        
        # 找到最新的日期文件夹
        latest_date_folder = max(date_folders, key=lambda d: datetime.strptime(d, '%Y_%m_%d'))
        print(f"Latest date folder: {latest_date_folder}")
        
        # 请求最新日期文件夹的 GitHub API
        latest_folder_url = f'https://api.github.com/repos/{REPO}/contents/{DATA_DIR}/{latest_date_folder}'
        response = requests.get(latest_folder_url)
        response.raise_for_status()
        files = response.json()
        
        # 查找最新 YAML 文件
        yaml_files = [f['name'] for f in files if f['name'].endswith('.yaml')]
        
        if not yaml_files:
            print("No YAML files found in the latest date folder.")
            return None
        
        # 获取最新的 YAML 文件 URL
        latest_yaml_file = yaml_files[-1]
        latest_yaml_url = f"https://raw.githubusercontent.com/{REPO}/main/{DATA_DIR}/{latest_date_folder}/{latest_yaml_file}"
        print(f"Latest YAML file URL: {latest_yaml_url}")
        return latest_yaml_url

    except requests.RequestException as e:
        print(f"Error fetching latest YAML file: {e}")
        return None

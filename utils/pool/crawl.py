import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

REPO_URL = 'https://github.com/changfengoss/pub'
DATA_DIR = 'data'

def get_latest_yaml_file():
    """获取最新 YAML 文件的 URL"""
    try:
        # 请求 data 目录页面
        response = requests.get(f"{REPO_URL}/tree/main/{DATA_DIR}")
        response.raise_for_status()
        
        # 解析 HTML 内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找日期文件夹
        date_folders = []
        for a in soup.find_all('a', href=True):
            if a['href'].startswith(f"{DATA_DIR}/"):
                folder_name = a['href'].split('/')[-1]
                if re.match(r'\d{4}_\d{2}_\d{2}', folder_name):
                    date_folders.append(folder_name)
        
        if not date_folders:
            print("No date folders found.")
            return None
        
        # 找到最新的日期文件夹
        latest_date_folder = max(date_folders, key=lambda d: datetime.strptime(d, '%Y_%m_%d'))
        
        # 请求最新日期文件夹页面
        response = requests.get(f"{REPO_URL}/tree/main/{DATA_DIR}/{latest_date_folder}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找最新 YAML 文件
        yaml_files = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.yaml')]
        
        if not yaml_files:
            print("No YAML files found in the latest date folder.")
            return None
        
        # 获取最新的 YAML 文件 URL
        latest_yaml_file = yaml_files[-1]
        latest_yaml_url = f"{REPO_URL}/raw/main/{latest_yaml_file}"
        return latest_yaml_url

    except requests.RequestException as e:
        print(f"Error fetching latest YAML file: {e}")
        return None

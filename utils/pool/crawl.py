import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

REPO_URL = 'https://github.com/changfengoss/pub'
RAW_URL = 'https://raw.githubusercontent.com/changfengoss/pub/main'
DATA_DIR = 'data'

def get_latest_yaml_file():
    """获取最新 YAML 文件的 URL"""
    try:
        # 请求 data 目录页面
        response = requests.get(f"{REPO_URL}/tree/main/{DATA_DIR}")
        response.raise_for_status()
        
        # 打印页面 HTML 内容以便调试
        print("Page HTML content for data directory:")
        print(response.text[:500])  # 打印前500字符
        
        # 解析 HTML 内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找日期文件夹
        date_folders = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(f"/changfengoss/pub/tree/main/{DATA_DIR}/"):
                folder_name = href.split('/')[-1]
                if re.match(r'\d{4}_\d{2}_\d{2}', folder_name):
                    date_folders.append(folder_name)
        
        if not date_folders:
            print("No date folders found.")
            return None
        
        # 打印找到的日期文件夹
        print(f"Found date folders: {date_folders}")
        
        # 找到最新的日期文件夹
        latest_date_folder = max(date_folders, key=lambda d: datetime.strptime(d, '%Y_%m_%d'))
        print(f"Latest date folder: {latest_date_folder}")
        
        # 请求最新日期文件夹页面
        response = requests.get(f"{REPO_URL}/tree/main/{DATA_DIR}/{latest_date_folder}")
        response.raise_for_status()
        
        # 打印页面 HTML 内容以便调试
        print(f"Page HTML content for latest date folder ({latest_date_folder}):")
        print(response.text[:500])  # 打印前500字符
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找最新 YAML 文件
        yaml_files = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.yaml')]
        
        if not yaml_files:
            print("No YAML files found in the latest date folder.")
            return None
        
        # 打印找到的 YAML 文件
        print(f"Found YAML files: {yaml_files}")
        
        # 获取最新的 YAML 文件 URL
        latest_yaml_file = yaml_files[-1]
        latest_yaml_url = f"{RAW_URL}/{latest_yaml_file.split('/')[-3]}/{latest_yaml_file.split('/')[-1]}"
        print(f"Latest YAML file URL: {latest_yaml_url}")
        return latest_yaml_url

    except requests.RequestException as e:
        print(f"Error fetching latest YAML file: {e}")
        return None

def fetch_yaml_file(url):
    """获取 YAML 文件内容"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to fetch YAML file. Error: {e}")
        return None

def process_yaml(yaml_content):
    """处理 YAML 内容"""
    try:
        import yaml
        data = yaml.safe_load(yaml_content)
        print("YAML data parsed successfully.")
        print(f"YAML Data: {data}")
    except yaml.YAMLError as e:
        print(f"Failed to parse YAML file. Error: {e}")

def main():
    yaml_url = get_latest_yaml_file()
    if yaml_url:
        yaml_content = fetch_yaml_file(yaml_url)
        if yaml_content:
            process_yaml(yaml_content)
        else:
            print("Could not fetch the YAML file.")
    else:
        print("Could not find the latest YAML file.")

if __name__ == "__main__":
    main()

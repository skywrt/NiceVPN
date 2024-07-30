import os
import requests
from datetime import datetime, timedelta

REPO = 'changfengoss/pub'
DATA_DIR = 'data'
GITHUB_API_URL = f'https://api.github.com/repos/{REPO}/contents/{DATA_DIR}'
PROCESSED_YAML_DIR = 'processed_yaml'

def get_date_folder_url(date_str):
    """获取指定日期文件夹的 GitHub API URL"""
    return f'{GITHUB_API_URL}/{date_str}'

def create_processed_yaml_dir():
    """创建存储已处理 YAML 文件记录的文件夹"""
    if not os.path.exists(PROCESSED_YAML_DIR):
        os.makedirs(PROCESSED_YAML_DIR)

def get_processed_file_name(date):
    """根据给定日期获取处理文件名"""
    return os.path.join(PROCESSED_YAML_DIR, f'processed_yaml_{date}.txt')

def save_processed_file(file_url):
    """保存新的 YAML 文件 URL 到记录中并下载文件"""
    create_processed_yaml_dir()  # 确保目录存在
    today_date = datetime.now().strftime('%Y_%m_%d')
    processed_file = get_processed_file_name(today_date)
    
    # 确保文件存在，如果文件夹或文件不存在则创建
    with open(processed_file, 'a') as file:
        file.write(file_url + '\n')
    print(f"Saved processed file URL: {file_url}")

    # 下载最新的 YAML 文件并保存到 processed_yaml 目录中
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        yaml_file_name = os.path.join(PROCESSED_YAML_DIR, os.path.basename(file_url))
        with open(yaml_file_name, 'wb') as file:
            file.write(response.content)
        print(f"Saved latest YAML file to {yaml_file_name}")
    except requests.RequestException as e:
        print(f"Error downloading YAML file from {file_url}: {e}")

def load_processed_files():
    """加载已处理的 YAML 文件列表"""
    today_date = datetime.now().strftime('%Y_%m_%d')
    processed_file = get_processed_file_name(today_date)
    if not os.path.exists(processed_file):
        return set()
    with open(processed_file, 'r') as file:
        return set(line.strip() for line in file)

def get_latest_yaml_file():
    """获取最新 YAML 文件的 URL"""
    try:
        # 请求 data 目录的 GitHub API
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()
        
        # 打印获取的文件列表进行调试
        print("Files in data directory:", files)
        
        # 获取今天和昨天的日期字符串
        today = datetime.now().strftime('%Y_%m_%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d')

        # 筛选出日期文件夹
        date_folders = [file for file in files if file['type'] == 'dir' and file['name'] in [today, yesterday]]
        if not date_folders:
            print("No date folders found for today or yesterday.")
            return None
        
        latest_date_folder = max(date_folders, key=lambda d: datetime.strptime(d['name'], '%Y_%m_%d'))
        latest_folder_url = get_date_folder_url(latest_date_folder['name'])
        print(f"Latest date folder: {latest_date_folder['name']}")
        
        # 请求最新日期文件夹的 GitHub API
        response = requests.get(latest_folder_url)
        response.raise_for_status()
        files = response.json()
        
        # 打印获取的文件列表进行调试
        print(f"Files in {latest_date_folder['name']} folder:", files)
        
        # 查找 YAML 文件并选择最新的文件（基于更新时间）
        yaml_files = [file for file in files if file['name'].endswith('.yaml')]
        if not yaml_files:
            print("No YAML files found in the latest date folder.")
            return None
        
        # 找到更新时间最新的 YAML 文件
        latest_yaml_file = max(yaml_files, key=lambda f: f['path'])
        
        if latest_yaml_file:
            latest_yaml_url = latest_yaml_file['download_url']
            print(f"Latest YAML file URL: {latest_yaml_url}")
            
            # 检查是否已经处理过
            processed_files = load_processed_files()
            if latest_yaml_url not in processed_files:
                # 如果没有处理过，则进行处理
                print(f"Processing new YAML file: {latest_yaml_url}")
                
                # 保存已处理的 YAML 文件 URL
                save_processed_file(latest_yaml_url)
            else:
                print(f"YAML file already processed: {latest_yaml_url}")

            return latest_yaml_url
        else:
            print("No YAML files found.")
            return None

    except requests.RequestException as e:
        print(f"Error fetching latest YAML file: {e}")
        return None

if __name__ == "__main__":
    get_latest_yaml_file()

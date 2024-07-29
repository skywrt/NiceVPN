import requests
from datetime import datetime, timedelta

REPO = 'changfengoss/pub'
DATA_DIR = 'data'
GITHUB_API_URL = f'https://api.github.com/repos/{REPO}/contents/{DATA_DIR}'

def get_date_folder_url(date_str):
    """获取指定日期文件夹的 GitHub API URL"""
    return f'{GITHUB_API_URL}/{date_str}'

def get_latest_yaml_file():
    """获取最新 YAML 文件的 URL"""
    try:
        # 请求 data 目录的 GitHub API
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()
        
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
        
        # 查找 YAML 文件并选择最新的文件（基于文件名）
        yaml_files = [file for file in files if file['name'].endswith('.yaml')]
        if not yaml_files:
            print("No YAML files found in the latest date folder.")
            return None
        
        # 假设文件名的时间戳排序是合理的
        latest_yaml_file = max(yaml_files, key=lambda f: f['name'])
        
        if latest_yaml_file:
            latest_yaml_url = latest_yaml_file['download_url']
            print(f"Latest YAML file URL: {latest_yaml_url}")
            return latest_yaml_url
        else:
            print("No YAML files found.")
            return None

    except requests.RequestException as e:
        print(f"Error fetching latest YAML file: {e}")
        return None

# 调用函数获取最新的 YAML 文件 URL
if __name__ == "__main__":
    get_latest_yaml_file()

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

def get_latest_yaml_path():
    """获取最新的 YAML 文件路径"""
    yaml_files = [f for f in os.listdir(PROCESSED_YAML_DIR) if f.endswith('.yaml')]
    if not yaml_files:
        return None
    return os.path.join(PROCESSED_YAML_DIR, max(yaml_files, key=lambda f: os.path.getctime(os.path.join(PROCESSED_YAML_DIR, f))))

def save_processed_file(file_url):
    """保存新的 YAML 文件 URL 到记录中并下载文件"""
    create_processed_yaml_dir()  # 确保目录存在
    latest_yaml_path = get_latest_yaml_path()

    try:
        response = requests.get(file_url)
        response.raise_for_status()
        yaml_file_name = os.path.basename(file_url)
        yaml_file_path = os.path.join(PROCESSED_YAML_DIR, yaml_file_name)

        # 删除旧的 YAML 文件
        if latest_yaml_path and os.path.exists(latest_yaml_path):
            os.remove(latest_yaml_path)

        # 保存新的 YAML 文件
        with open(yaml_file_path, 'wb') as file:
            file.write(response.content)

    except requests.RequestException as e:
        print(f"Error downloading YAML file from {file_url}: {e}")

def load_processed_files():
    """加载已处理的 YAML 文件列表"""
    processed_file = get_processed_file_name()
    if not os.path.exists(processed_file):
        return set()
    with open(processed_file, 'r') as file:
        return set(line.strip() for line in file)

def get_processed_file_name():
    """获取处理文件的文件名"""
    today_date = datetime.now().strftime('%Y_%m_%d')
    return os.path.join(PROCESSED_YAML_DIR, f'processed_yaml_{today_date}.txt')

def save_processed_file_record(file_url):
    """记录处理过的 YAML 文件 URL"""
    processed_file = get_processed_file_name()
    create_processed_yaml_dir()  # 确保目录存在

    # 先保存文件
    with open(processed_file, 'a') as file:
        file.write(file_url + '\n')

    # 保留最新的三个 TXT 文件
    keep_latest_processed_files()

def keep_latest_processed_files():
    """保留最新的三个 TXT 文件"""
    txt_files = [f for f in os.listdir(PROCESSED_YAML_DIR) if f.endswith('.txt')]
    if len(txt_files) > 3:
        # 按文件创建时间排序，删除最旧的文件
        txt_files.sort(key=lambda f: os.path.getctime(os.path.join(PROCESSED_YAML_DIR, f)))
        for file_to_delete in txt_files[:-3]:  # 删除多余的文件
            os.remove(os.path.join(PROCESSED_YAML_DIR, file_to_delete))

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
            return None
        
        latest_date_folder = max(date_folders, key=lambda d: datetime.strptime(d['name'], '%Y_%m_%d'))
        latest_folder_url = get_date_folder_url(latest_date_folder['name'])
        
        # 请求最新日期文件夹的 GitHub API
        response = requests.get(latest_folder_url)
        response.raise_for_status()
        files = response.json()

        # 查找 YAML 文件
        yaml_files = [file for file in files if file['name'].endswith('.yaml')]
        if not yaml_files:
            return None
        
        # 获取已处理的文件 URL 集合
        processed_files = load_processed_files()
        
        # 过滤出未处理过的 YAML 文件
        new_yaml_files = [file for file in yaml_files if file['download_url'] not in processed_files]
        
        if not new_yaml_files:
            return None
        
        # 选择第一个新 YAML 文件
        latest_yaml_file = new_yaml_files[0]
        latest_yaml_url = latest_yaml_file['download_url']
        
        # 保存已处理的 YAML 文件 URL
        save_processed_file_record(latest_yaml_url)
        save_processed_file(latest_yaml_url)
        
        return latest_yaml_url

    except requests.RequestException as e:
        print(f"Error fetching latest YAML file: {e}")
        return None

if __name__ == "__main__":
    get_latest_yaml_file()

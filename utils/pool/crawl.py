import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def get_latest_folder_url(repo_url):
    # 请求主数据目录的页面
    response = requests.get(f'{repo_url}/tree/main/data')
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有日期文件夹链接
    folder_links = soup.find_all('a', class_='js-navigation-open')
    folders = [(link.get_text(), f"{repo_url}{link['href']}") for link in folder_links if re.match(r'\d{4}_\d{2}_\d{2}', link.get_text())]
    
    # 筛选出最新的文件夹
    latest_folder = None
    latest_date = datetime.min
    
    for folder_name, folder_url in folders:
        folder_date = datetime.strptime(folder_name, '%Y_%m_%d')
        if folder_date > latest_date:
            latest_date = folder_date
            latest_folder = folder_url
            
    return latest_folder

def get_latest_yaml_file_url(folder_url):
    # 请求最新日期文件夹的页面
    response = requests.get(folder_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有YAML文件链接
    file_links = soup.find_all('a', class_='js-navigation-open')
    yaml_files = [(link.get_text(), f"{repo_url}{link['href']}") for link in file_links if link.get_text().endswith('.yaml')]
    
    # 筛选出最新的YAML文件
    latest_file = None
    latest_timestamp = datetime.min
    
    for file_name, file_url in yaml_files:
        # 文件名包含日期时间的格式（例如 timestamp），需要根据实际文件名格式调整
        match = re.search(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}', file_name)
        if match:
            file_timestamp = datetime.strptime(match.group(0), '%Y_%m_%d_%H_%M_%S')
            if file_timestamp > latest_timestamp:
                latest_timestamp = file_timestamp
                latest_file = file_url
    
    return latest_file

repo_url = 'https://github.com/changfengoss/pub'
latest_folder_url = get_latest_folder_url(repo_url)

if latest_folder_url:
    latest_yaml_file_url = get_latest_yaml_file_url(latest_folder_url)
    if latest_yaml_file_url:
        # 下载最新的YAML文件
        yaml_response = requests.get(latest_yaml_file_url)
        yaml_response.raise_for_status()
        
        # 打印文件内容
        data = yaml_response.text
        print(f"最新的YAML文件内容如下:\n{data}")
    else:
        print("没有找到最新的YAML文件")
else:
    print("没有找到最新的日期文件夹")

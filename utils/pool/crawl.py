import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
import re

GITHUB_REPO_URL = "https://github.com/changfengoss/pub"
DATA_FOLDER_URL = f"{GITHUB_REPO_URL}/tree/main/data"

def get_soup(url):
    """获取页面的 BeautifulSoup 对象"""
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def get_latest_date():
    """获取最新的日期文件夹"""
    soup = get_soup(DATA_FOLDER_URL)
    links = soup.find_all('a', href=True)
    dates = []

    for link in links:
        match = re.match(r'data/(\d{4}_\d{2}_\d{2})', link['href'])
        if match:
            dates.append(match.group(1))

    dates.sort(reverse=True)
    return dates[0] if dates else None

def get_latest_yaml(date_folder):
    """获取最新的 YAML 文件"""
    date_folder_url = f"{DATA_FOLDER_URL}/{date_folder}"
    soup = get_soup(date_folder_url)
    links = soup.find_all('a', href=True)
    yaml_files = [link['href'] for link in links if link['href'].endswith('.yaml')]

    if not yaml_files:
        return None

    # Assuming the latest file is the last in the list (may need more logic based on naming)
    latest_yaml_file = yaml_files[-1]
    return latest_yaml_file

def get_latest_yaml_file():
    """获取最新的 YAML 文件路径"""
    latest_date = get_latest_date()
    if not latest_date:
        print("No date folders found.")
        return None

    latest_yaml = get_latest_yaml(latest_date)
    if not latest_yaml:
        print("No YAML files found.")
        return None

    return f"{GITHUB_REPO_URL}/blob/main/{latest_yaml}"

if __name__ == "__main__":
    latest_yaml_url = get_latest_yaml_file()
    if latest_yaml_url:
        print("Latest YAML URL:", latest_yaml_url)
    else:
        print("Failed to get the latest YAML file.")

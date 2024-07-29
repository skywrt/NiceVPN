import requests
import yaml
import time

def fetch(proxy_list, filename):
    try:
        current_date = time.strftime("%Y_%m_%d", time.localtime())
        baseurl = 'https://raw.githubusercontent.com/changfengoss/pub/main/data/'
        url = f"{baseurl}{current_date}/{filename}"
        print(f"Fetching URL: {url}")  # 调试输出
        
        # 请求 YAML 文件
        response = requests.get(url=url, timeout=30)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析 YAML 文件
        working = yaml.safe_load(response.text)
        if not isinstance(working, dict) or 'proxies' not in working:
            print(f"Unexpected YAML format or 'proxies' key missing in {filename}")
            return
        
        data_out = []
        for x in working['proxies']:
            data_out.append(x)
        
        # 将结果添加到 proxy_list
        proxy_list.append(data_out)
        print(f"Successfully fetched and processed {filename}")
    
    except requests.RequestException as e:
        print(f"Error fetching file {filename}: {e}")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {filename}: {e}")

# 示例用法
if __name__ == '__main__':
    from multiprocessing import Manager

    with Manager() as manager:
        proxy_list = manager.list()
        # 这里我们假设 'latest_file.yaml' 是我们想要处理的文件名
        fetch(proxy_list, 'latest_file.yaml')  # 替换 'latest_file.yaml' 为实际文件名

        # 打印 proxy_list 内容
        print(list(proxy_list))

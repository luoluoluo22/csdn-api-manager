"""
配置文件
"""

import os
import json
from pathlib import Path

# 默认Chrome路径
DEFAULT_CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def get_chrome_path() -> str:
    """获取Chrome浏览器路径
    
    优先级：
    1. 环境变量 CHROME_PATH
    2. config.json中的chrome_path
    3. 默认路径
    """
    # 1. 检查环境变量
    chrome_path = os.getenv('CHROME_PATH')
    if chrome_path:
        return chrome_path
        
    # 2. 检查配置文件
    config_file = Path("config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'chrome_path' in config:
                    return config['chrome_path']
        except:
            pass
            
    # 3. 使用默认路径
    return DEFAULT_CHROME_PATH 
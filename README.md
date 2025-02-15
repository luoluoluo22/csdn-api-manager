# CSDN API Manager

一个基于浏览器自动化的CSDN API客户端，用于获取CSDN用户信息和消息通知等数据。

## 功能特性

- 使用浏览器自动化技术，无需处理复杂的API签名
- 支持获取用户基本信息
- 支持获取未读消息数量
- 自动处理登录状态和Cookie管理

## 安装要求

- Python 3.8+
- Google Chrome 浏览器
- 以下Python包：
  - pyppeteer
  - loguru
  - asyncio

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置：
复制配置文件模板并根据需要修改：
```bash
cp config.example.json config.json
```

配置文件说明：
```json
{
    "chrome_path": "Chrome浏览器路径",
    "cookies_file": "cookies.json",
    "log_level": "INFO",
    "headless": false,
    "window_size": {
        "width": 1366,
        "height": 768
    }
}
```

3. 首次使用需要登录：
```bash
python -m src.csdn_api.login_analysis
```
按照提示使用微信扫码登录，登录成功后cookies会自动保存。

4. 使用示例：
```python
import asyncio
from src.csdn_api.client import CSDNClient

async def main():
    # 指定Chrome浏览器路径
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    client = CSDNClient(chrome_path=chrome_path)
    
    try:
        # 获取用户信息
        user_info = await client.get_user_info()
        print("用户信息:", user_info)
        
        # 获取未读消息数量
        msg_count = await client.get_unread_message_count()
        print("未读消息:", msg_count)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## API文档

### CSDNClient

主要的API客户端类。

#### 初始化参数

- `chrome_path`: Chrome浏览器可执行文件路径
- `cookies_file`: Cookie文件路径（可选，默认为"cookies.json"）

#### 方法

##### get_user_info()
获取用户基本信息。

返回示例：
```python
{
    'code': 200,
    'msg': 'success',
    'data': {
        'general': {
            'avatar': '头像URL',
            'codeAge': 2363,
            'codeAgeModule': {
                'desc': '码龄6年'
            }
        },
        'basic': {
            'id': '用户ID',
            'nickname': '用户昵称'
        }
    }
}
```

##### get_unread_message_count()
获取未读消息数量。

返回示例：
```python
{
    'code': '0',
    'message': 'success',
    'data': {
        'thumb_up': 0,
        'im': 6,
        'totalCount': 6
    }
}
```

## 注意事项

1. 首次使用前必须运行`login_analysis.py`完成登录
2. 确保Chrome浏览器已安装且路径正确
3. 如果遇到认证失败，请重新运行`login_analysis.py`进行登录
4. 不要将包含敏感信息的文件（如cookies.json）提交到代码仓库

## 开发计划

- [ ] 添加更多API支持
- [ ] 优化错误处理
- [ ] 添加自动重试机制
- [ ] 支持更多的登录方式

## 许可证

MIT License 
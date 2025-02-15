# CSDN API Manager

一个基于浏览器自动化的CSDN API客户端，用于获取CSDN用户信息和消息通知等数据。

## 功能特性

- 使用浏览器自动化技术，无需处理复杂的API签名
- 支持获取用户基本信息
- 支持获取未读消息数量
- 支持获取文章列表
- 自动处理登录状态和Cookie管理

## 安装要求

- Python 3.8+
- Google Chrome 浏览器
- 以下Python包：
  - pyppeteer
  - loguru
  - asyncio

## 环境变量

可以通过以下方式配置Chrome浏览器路径（按优先级排序）：

1. 环境变量：
```bash
# Windows
set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"

# Linux/Mac
export CHROME_PATH="/usr/bin/google-chrome"
```

2. 配置文件 `config.json`：
```json
{
    "chrome_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
}
```

3. 默认路径：`C:\Program Files\Google\Chrome\Application\chrome.exe`

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
    client = CSDNClient()  # 不再需要手动指定chrome_path
    
    try:
        # 获取用户信息
        user_info = await client.get_user_info()
        print("用户信息:", user_info)
        
        # 获取未读消息数量
        msg_count = await client.get_unread_message_count()
        print("未读消息:", msg_count)
        
        # 获取文章列表
        articles = await client.get_article_list(page=1, size=20)
        for article in articles['data']['list']:
            print(f"\n文章标题: {article['title']}")
            print(f"链接: {article['url']}")
            print(f"描述: {article['description']}")
            print(f"阅读数: {article['viewCount']}")
            
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## API文档

### CSDNClient

主要的API客户端类。

#### 初始化参数

- `chrome_path`: Chrome浏览器可执行文件路径（可选）
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

##### get_article_list(page: int = 1, size: int = 20, status: str = "all")
获取文章列表。

参数：
- `page`: 页码，从1开始
- `size`: 每页数量
- `status`: 文章状态，可选值：all（全部）、published（已发布）、draft（草稿）

返回示例：
```python
{
    'code': 200,
    'message': 'success',
    'data': {
        'list': [
            {
                'articleId': 144249054,
                'title': '文章标题',
                'description': '文章描述',
                'url': '文章链接',
                'type': 1,
                'viewCount': 阅读数,
                'commentCount': 评论数,
                'diggCount': 点赞数,
                'publishTime': '发布时间'
            }
        ],
        'total': 总文章数,
        'pageSize': 每页数量,
        'currentPage': 当前页码
    }
}
```

## 注意事项

1. 首次使用前必须运行`login_analysis.py`完成登录
2. 确保Chrome浏览器已安装且路径正确
3. 如果遇到认证失败，请重新运行`login_analysis.py`进行登录
4. 不要将包含敏感信息的文件（如cookies.json）提交到代码仓库

## 开发计划

- [x] 添加文章列表API支持
- [ ] 优化错误处理
- [ ] 添加自动重试机制
- [ ] 支持更多的登录方式

## 许可证

MIT License 
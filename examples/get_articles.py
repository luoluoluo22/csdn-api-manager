"""
获取文章列表示例
"""

import asyncio
from loguru import logger
from src.csdn_api.client import CSDNClient

async def main():
    """主函数"""
    logger.info("开始获取文章列表...")
    client = None
    
    try:
        # 指定Chrome浏览器路径
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        client = CSDNClient(chrome_path=chrome_path)
        
        # 获取第一页文章列表
        articles = await client.get_article_list(page=1, size=20)
        
        # 打印文章信息
        if articles and 'data' in articles:
            for article in articles['data']['list']:
                print(f"\n文章标题: {article['title']}")
                print(f"发布时间: {article['publishTime']}")
                print(f"阅读数: {article['viewCount']}")
                print(f"评论数: {article['commentCount']}")
                print(f"点赞数: {article['diggCount']}")
                print("-" * 50)
        
    except Exception as e:
        logger.error(f"获取文章列表失败: {str(e)}")
    finally:
        if client:
            await client.close()
        
    logger.info("获取完成！")

if __name__ == "__main__":
    # 使用新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close() 
"""
搜索示例
"""

import asyncio
from loguru import logger
from src.csdn_api.client import CSDNClient

async def main():
    """主函数"""
    logger.info("开始搜索...")
    client = None
    
    try:
        client = CSDNClient()
        
        # 搜索Python相关内容
        results = await client.search(
            keyword="Python爬虫",
            page=1,
            scope="all"
        )
        
        # 打印搜索结果
        if results and 'result_vos' in results:
            result_list = results['result_vos']
            print(f"\n找到 {len(result_list)} 条结果:")
            
            for item in result_list:
                print("\n" + "=" * 50)
                print(f"标题: {item.get('title', 'N/A')}")
                print(f"链接: {item.get('url', 'N/A')}")
                print(f"作者: {item.get('nickname', 'N/A')}")
                print(f"发布时间: {item.get('created_at', 'N/A')}")
                print(f"浏览量: {item.get('view_count', 'N/A')}")
                print(f"描述: {item.get('description', 'N/A')}")
                print("=" * 50)
        
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
    finally:
        if client:
            await client.close()
        
    logger.info("搜索完成！")

if __name__ == "__main__":
    # 使用新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close() 
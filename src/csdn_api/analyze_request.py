"""
分析CSDN API请求的脚本
用于捕获和分析实际的API请求
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from pyppeteer import launch
from loguru import logger

class RequestAnalyzer:
    def __init__(self):
        self.requests_log = []
        # 定义需要分析的API端点
        self.target_urls = [
            'bizapi.csdn.net/user-api/user/getUserInfoByToken',
            'bizapi.csdn.net/community-personal/v1/get-personal-info',
            'bizapi.csdn.net/user-api/user/profile/info',
            'msg.csdn.net/v1/web/message/view/unread'
        ]
        
    async def intercept_request(self, request):
        """拦截并分析请求"""
        try:
            # 检查是否是目标请求
            if any(url in request.url for url in self.target_urls):
                # 获取请求体
                post_data = None
                if request.method == 'POST':
                    try:
                        post_data = request.postData
                    except:
                        pass
                
                # 获取关键请求头
                important_headers = [
                    'x-ca-key',
                    'x-ca-nonce',
                    'x-ca-signature',
                    'x-ca-signature-headers',
                    'x-ca-timestamp'
                ]
                
                headers = dict(request.headers)
                key_headers = {k: v for k, v in headers.items() if k.lower() in important_headers}
                
                req_data = {
                    "url": request.url,
                    "method": request.method,
                    "headers": headers,
                    "key_headers": key_headers,
                    "timestamp": datetime.now().isoformat(),
                    "post_data": post_data
                }
                
                # 保存请求信息
                self.requests_log.append(req_data)
                
                # 打印详细信息
                logger.info(f"\n捕获目标请求: {request.method} {request.url}")
                logger.info("关键请求头:")
                for key, value in key_headers.items():
                    logger.info(f"{key}: {value}")
                    
                # 尝试重建签名字符串
                try:
                    path = request.url.split('.net')[-1]
                    signature_parts = [
                        request.method,
                        path
                    ]
                    
                    # 添加签名头部
                    if 'x-ca-signature-headers' in key_headers:
                        header_names = key_headers['x-ca-signature-headers'].split(',')
                        for name in header_names:
                            if name in key_headers:
                                signature_parts.append(f"{name}:{key_headers[name]}")
                    
                    # 添加请求体
                    if post_data:
                        signature_parts.append(post_data)
                        
                    signature_string = '\n'.join(signature_parts)
                    logger.info(f"\n推测的签名字符串:\n{signature_string}")
                    
                except Exception as e:
                    logger.error(f"重建签名字符串时出错: {str(e)}")
                    
                if post_data:
                    logger.info(f"请求体: {post_data}")
                    
        except Exception as e:
            logger.error(f"拦截请求时出错: {str(e)}")
            
    async def intercept_response(self, response):
        """拦截并分析响应"""
        try:
            if any(url in response.url for url in self.target_urls):
                logger.info(f"\n响应信息:")
                logger.info(f"URL: {response.url}")
                logger.info(f"状态码: {response.status}")
                try:
                    resp_text = await response.text()
                    logger.info(f"响应内容: {resp_text}")
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"拦截响应时出错: {str(e)}")
            
    async def analyze(self):
        """分析请求"""
        browser = await launch(
            headless=False,
            executablePath="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            args=['--no-sandbox', '--window-size=1366,768'],
            defaultViewport={'width': 1366, 'height': 768}
        )
        
        try:
            page = await browser.newPage()
            
            # 监听请求和响应
            page.on('request', lambda req: asyncio.ensure_future(self.intercept_request(req)))
            page.on('response', lambda res: asyncio.ensure_future(self.intercept_response(res)))
            
            # 加载cookies
            cookies_file = Path("cookies.json")
            if cookies_file.exists():
                with open(cookies_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                await page.setCookie(*cookies)
                logger.info(f"已加载 {len(cookies)} 个cookies")
            
            # 访问用户中心
            logger.info("\n正在访问用户中心...")
            await page.goto('https://i.csdn.net/')
            await asyncio.sleep(3)
            
            # 访问个人资料页
            logger.info("\n正在访问个人资料页...")
            await page.goto('https://i.csdn.net/#/user-center/profile')
            await asyncio.sleep(3)
            
            # 访问消息中心
            logger.info("\n正在访问消息中心...")
            await page.goto('https://i.csdn.net/#/msg/index')
            await asyncio.sleep(3)
            
            # 等待用户手动操作
            logger.info("\n=== 请在浏览器中操作 ===")
            logger.info("1. 请尝试刷新页面或点击不同的菜单")
            logger.info("2. 观察网络请求")
            logger.info("3. 完成后请关闭浏览器窗口\n")
            
            try:
                await page.waitForSelector('body', {'timeout': 300000})  # 等待5分钟
            except:
                pass
            
            # 保存请求日志
            if self.requests_log:
                output_file = Path('api_requests.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.requests_log, f, ensure_ascii=False, indent=2)
                logger.info(f"\n请求日志已保存到: {output_file.absolute()}")
                logger.info(f"共捕获 {len(self.requests_log)} 个目标请求")
            else:
                logger.warning("未捕获到任何目标请求")
            
        except Exception as e:
            logger.error(f"分析过程出错: {str(e)}")
        finally:
            await browser.close()

def main():
    """主函数"""
    logger.info("开始分析API请求...")
    analyzer = RequestAnalyzer()
    
    try:
        # 使用新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(analyzer.analyze())
        loop.close()
    except Exception as e:
        logger.error(f"运行出错: {str(e)}")
    finally:
        logger.info("分析完成！")

if __name__ == "__main__":
    main() 
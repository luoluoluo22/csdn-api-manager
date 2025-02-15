"""
CSDN 登录流程分析脚本
用于捕获和分析 CSDN 的登录请求
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from pyppeteer import launch
from loguru import logger

# 定义关键域名列表
IMPORTANT_DOMAINS = [
    'bizapi.csdn.net',
    'gw.csdn.net',
    'passport.csdn.net',
    'api.csdn.net'
]

class CSDNLoginAnalyzer:
    def __init__(self):
        self.requests_log: List[Dict] = []
        self.cookies_file = Path("cookies.json")
        self.requests_file = Path("login_requests.json")
        
    async def save_request(self, request):
        """保存请求信息，仅保存关键请求"""
        try:
            # 检查是否是关键域名
            if not any(domain in request.url for domain in IMPORTANT_DOMAINS):
                return
                
            # 忽略静态资源
            if request.resourceType in ['image', 'stylesheet', 'font', 'media']:
                return
                
            # 获取请求信息
            req_data = {
                "url": request.url,
                "method": request.method,
                "headers": dict(request.headers),  # 保存所有请求头
                "timestamp": datetime.now().isoformat(),
                "resourceType": request.resourceType,
            }
            
            # 如果是POST请求，尝试获取请求体
            if request.method == "POST":
                try:
                    post_data = request.postData
                    if post_data:
                        req_data["postData"] = post_data
                except:
                    pass
            
            self.requests_log.append(req_data)
            logger.info(f"捕获API请求: {request.method} {request.url}")
            logger.debug(f"请求头: {dict(request.headers)}")
            
        except Exception as e:
            logger.error(f"保存请求时出错: {str(e)}")
    
    async def check_login_status(self, page) -> bool:
        """检查是否已登录"""
        try:
            # 访问用户中心
            await page.goto('https://i.csdn.net/')
            await asyncio.sleep(5)  # 增加等待时间
            
            # 获取当前页面的 cookies
            cookies = await page.cookies()
            
            # 检查关键 cookie 是否存在
            important_cookies = ['UserName', 'UserToken', 'uuid_tt_dd']
            found_cookies = [cookie['name'] for cookie in cookies]
            
            if any(cookie in found_cookies for cookie in important_cookies):
                logger.info(f"检测到登录状态 cookies: {[c for c in found_cookies if c in important_cookies]}")
                return True
                
            # 如果没有找到关键 cookie，检查 URL
            current_url = page.url
            if 'passport.csdn.net/login' in current_url:
                logger.warning("未检测到登录状态，当前在登录页面")
                return False
                
            # 尝试获取用户信息接口的响应
            try:
                response = await page.evaluate('''() => {
                    return fetch('https://bizapi.csdn.net/community-personal/v1/get-personal-info', {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json, text/plain, */*'
                        }
                    }).then(res => res.status === 200);
                }''')
                if response:
                    logger.info("用户信息接口响应正常，已登录")
                    return True
            except:
                pass
                
            logger.warning("未能确认登录状态")
            return False
                
        except Exception as e:
            logger.error(f"检查登录状态时出错: {str(e)}")
            return False
    
    async def save_cookies(self, page):
        """保存cookies到文件"""
        try:
            cookies = await page.cookies()
            # 保存所有cookies，不过滤
            if cookies:
                with open(self.cookies_file, 'w', encoding='utf-8') as f:
                    json.dump(cookies, f, ensure_ascii=False, indent=2)
                logger.info(f"Cookies已保存到: {self.cookies_file} (共 {len(cookies)} 个)")
            else:
                logger.warning("没有找到任何cookies！")
                
        except Exception as e:
            logger.error(f"保存cookies时出错: {str(e)}")
    
    async def analyze_login(self):
        """分析登录流程"""
        browser = await launch(
            headless=False,
            executablePath="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            args=['--no-sandbox', '--window-size=1366,768'],
            defaultViewport={'width': 1366, 'height': 768}
        )
        
        try:
            page = await browser.newPage()
            
            # 监听所有网络请求
            page.on('request', lambda req: asyncio.ensure_future(self.save_request(req)))
            
            # 直接访问登录页面
            logger.info("正在打开登录页面...")
            await page.goto('https://passport.csdn.net/login')
            await asyncio.sleep(2)
            
            logger.info("\n=== 请按照以下步骤操作 ===")
            logger.info("1. 请使用微信扫码登录")
            logger.info("2. 登录成功后，脚本将自动继续")
            logger.info("3. 如果页面刷新太快，请重新运行脚本")
            logger.info("4. 您有充足的时间完成登录，请不要着急\n")
            
            # 等待登录成功，增加检查间隔时间
            login_success = False
            max_attempts = 60  # 最多等待10分钟
            for _ in range(max_attempts):
                if await self.check_login_status(page):
                    login_success = True
                    break
                logger.info("等待登录完成...")
                await asyncio.sleep(10)  # 每10秒检查一次
            
            if not login_success:
                logger.error("登录等待超时，请重新运行脚本")
                return
                    
            # 访问用户中心
            logger.info("登录成功！正在访问用户中心...")
            await page.goto('https://i.csdn.net/')
            await asyncio.sleep(5)  # 增加等待时间
            
            # 访问个人资料页
            logger.info("正在访问个人资料页...")
            await page.goto('https://i.csdn.net/#/user-center/profile')
            await asyncio.sleep(5)  # 增加等待时间
            
            # 保存cookies
            await self.save_cookies(page)
            
            # 保存请求日志
            if self.requests_log:
                with open(self.requests_file, 'w', encoding='utf-8') as f:
                    json.dump(self.requests_log, f, ensure_ascii=False, indent=2)
                logger.info(f"API请求日志已保存到: {self.requests_file}")
            
            logger.info("\n=== 数据采集完成 ===")
            logger.info("1. cookies已保存")
            logger.info("2. 请求日志已保存")
            logger.info("3. 您可以关闭浏览器窗口了\n")
            
            # 等待用户关闭浏览器
            try:
                await page.waitForSelector('body', {'timeout': 300000})
            except:
                pass
            
        except Exception as e:
            logger.error(f"分析过程出错: {str(e)}")
        finally:
            await browser.close()

def main():
    """主函数"""
    logger.info("开始分析CSDN认证流程...")
    analyzer = CSDNLoginAnalyzer()
    
    # 使用新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(analyzer.analyze_login())
    loop.close()
    
    logger.info("分析完成！")

if __name__ == "__main__":
    main() 
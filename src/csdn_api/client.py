"""
CSDN API 客户端
处理与 CSDN 的所有交互
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from loguru import logger
from pyppeteer import launch
from src.csdn_api.exceptions import CSDNAuthError, CSDNAPIError
from src.csdn_api.config import get_chrome_path

class CSDNClient:
    """CSDN API 客户端类"""
    
    def __init__(self, chrome_path: str = None, cookies_file: str = None):
        """初始化CSDN API客户端
        
        Args:
            chrome_path (str, optional): Chrome浏览器路径，如果不指定则从环境变量或配置文件获取
            cookies_file (str, optional): cookies文件路径
        """
        self.chrome_path = chrome_path or get_chrome_path()
        self.cookies_file = Path(cookies_file) if cookies_file else Path("cookies.json")
        self.browser = None
        self.page = None
        
    async def init(self):
        """初始化浏览器"""
        if not self.browser:
            logger.info("启动浏览器...")
            try:
                self.browser = await launch(
                    headless=True,
                    executablePath=self.chrome_path,
                    args=['--no-sandbox', '--window-size=1366,768'],
                    defaultViewport={'width': 1366, 'height': 768}
                )
                
                self.page = await self.browser.newPage()
                
                # 加载cookies
                if self.cookies_file.exists():
                    try:
                        with open(self.cookies_file, 'r', encoding='utf-8') as f:
                            cookies = json.load(f)
                        await self.page.setCookie(*cookies)
                        logger.info(f"已加载 {len(cookies)} 个cookies")
                    except Exception as e:
                        logger.error(f"加载cookies失败: {str(e)}")
                        
            except Exception as e:
                logger.error(f"浏览器启动失败: {str(e)}")
                if self.browser:
                    await self.browser.close()
                self.browser = None
                self.page = None
                raise
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
            
    async def get_user_info(self) -> Dict:
        """获取用户基本信息
        
        Returns:
            Dict: 用户信息
            
        Raises:
            CSDNAuthError: 认证失败时抛出
            CSDNAPIError: API调用失败时抛出
        """
        await self.init()
        
        try:
            logger.info("正在获取用户信息...")
            
            # 先访问页面
            await self.page.goto('https://i.csdn.net/#/user-center/profile')
            await asyncio.sleep(2)  # 等待页面基本加载
            
            # 创建一个Future对象来存储响应
            response_future = asyncio.Future()
            
            def handle_response(response):
                asyncio.ensure_future(process_response(response))
                
            async def process_response(response):
                if response.url == 'https://bizapi.csdn.net/community-personal/v1/get-personal-info':
                    try:
                        json_data = await response.json()
                        if not response_future.done():
                            response_future.set_result(json_data)
                    except Exception as e:
                        if not response_future.done():
                            response_future.set_exception(e)
                        
            # 监听响应
            self.page.on('response', handle_response)
            
            # 刷新页面触发API请求
            await self.page.reload()
            
            # 等待响应数据或超时
            try:
                response_data = await asyncio.wait_for(response_future, timeout=5.0)
                logger.info(f"获取用户信息成功: {response_data}")
                return response_data
            except asyncio.TimeoutError:
                raise CSDNAPIError("获取用户信息超时")
            
        except Exception as e:
            if isinstance(e, CSDNAuthError):
                raise
            logger.error(f"获取用户信息失败: {str(e)}")
            raise CSDNAPIError(f"API调用失败: {str(e)}")
            
    async def get_unread_message_count(self) -> Dict:
        """获取未读消息数量
        
        Returns:
            Dict: 包含未读消息数量的响应
            
        Raises:
            CSDNAuthError: 认证失败时抛出
            CSDNAPIError: API调用失败时抛出
        """
        await self.init()
        
        try:
            logger.info("正在获取未读消息数量...")
            
            # 先访问页面
            await self.page.goto('https://i.csdn.net/#/msg/index')
            await asyncio.sleep(2)  # 等待页面基本加载
            
            # 创建一个Future对象来存储响应
            response_future = asyncio.Future()
            
            def handle_response(response):
                asyncio.ensure_future(process_response(response))
                
            async def process_response(response):
                if response.url == 'https://msg.csdn.net/v1/web/message/view/unread':
                    try:
                        json_data = await response.json()
                        if not response_future.done():
                            response_future.set_result(json_data)
                    except Exception as e:
                        if not response_future.done():
                            response_future.set_exception(e)
                        
            # 监听响应
            self.page.on('response', handle_response)
            
            # 刷新页面触发API请求
            await self.page.reload()
            
            # 等待响应数据或超时
            try:
                response_data = await asyncio.wait_for(response_future, timeout=5.0)
                logger.info(f"获取未读消息数量成功: {response_data}")
                return response_data
            except asyncio.TimeoutError:
                raise CSDNAPIError("获取未读消息数量超时")
            
        except Exception as e:
            if isinstance(e, CSDNAuthError):
                raise
            logger.error(f"获取未读消息数量失败: {str(e)}")
            raise CSDNAPIError(f"API调用失败: {str(e)}")

    async def check_login_status(self) -> bool:
        """检查登录状态
        
        Returns:
            bool: 是否已登录
        """
        try:
            await self.init()
            await self.page.goto('https://i.csdn.net/')
            await asyncio.sleep(2)
            
            current_url = self.page.url
            if 'passport.csdn.net/login' in current_url:
                return False
                
            cookies = await self.page.cookies()
            important_cookies = ['UserName', 'UserToken', 'uuid_tt_dd']
            found_cookies = [cookie['name'] for cookie in cookies]
            
            return any(cookie in found_cookies for cookie in important_cookies)
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            return False 

    async def get_article_list(self, page: int = 1, size: int = 20, status: str = "all") -> Dict:
        """获取文章列表
        
        Args:
            page: 页码，从1开始
            size: 每页数量
            status: 文章状态，可选值：all（全部）、published（已发布）、draft（草稿）
            
        Returns:
            Dict: 文章列表响应
            
        Raises:
            CSDNAuthError: 认证失败时抛出
            CSDNAPIError: API调用失败时抛出
        """
        await self.init()
        
        try:
            logger.info(f"正在获取文章列表... 第{page}页，每页{size}条，状态：{status}")
            
            # 先获取用户信息
            user_info = await self.get_user_info()
            if not user_info or 'data' not in user_info or 'basic' not in user_info['data']:
                raise CSDNAPIError("无法获取用户信息")
            
            user_id = user_info['data']['basic']['id']
            
            # 先访问博客主页
            blog_url = f'https://blog.csdn.net/{user_id}'
            logger.info(f"访问博客主页: {blog_url}")
            await self.page.goto(blog_url)
            await asyncio.sleep(2)  # 等待页面加载
            
            # 创建一个Future对象来存储响应
            response_future = asyncio.Future()
            
            def handle_response(response):
                asyncio.ensure_future(process_response(response))
                
            async def process_response(response):
                if 'get-business-list' in response.url:
                    try:
                        json_data = await response.json()
                        if not response_future.done():
                            response_future.set_result(json_data)
                    except Exception as e:
                        logger.error(f"解析响应失败: {str(e)}")
                        try:
                            text = await response.text()
                            logger.error(f"响应内容: {text}")
                        except:
                            pass
                        if not response_future.done():
                            response_future.set_exception(e)
            
            # 监听响应
            self.page.on('response', handle_response)
            
            # 使用evaluate执行API请求
            logger.info("执行API请求...")
            await self.page.evaluate(f'''async () => {{
                const response = await fetch('https://blog.csdn.net/community/home-api/v1/get-business-list?page={page}&size={size}&businessType=blog&orderby=&noMore=false&year=&month=&username={user_id}', {{
                    method: 'GET',
                    headers: {{
                        'accept': 'application/json, text/plain, */*',
                        'referer': '{blog_url}',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    }},
                    credentials: 'include'
                }});
                return response.json();
            }}''')
            
            # 等待响应数据或超时
            try:
                response_data = await asyncio.wait_for(response_future, timeout=10.0)
                logger.info(f"获取文章列表成功: {response_data}")
                return response_data
            except asyncio.TimeoutError:
                raise CSDNAPIError("获取文章列表超时")
            
        except Exception as e:
            if isinstance(e, CSDNAuthError):
                raise
            logger.error(f"获取文章列表失败: {str(e)}")
            raise CSDNAPIError(f"API调用失败: {str(e)}")

    async def search(self, keyword: str, page: int = 1, scope: str = "all") -> Dict:
        """搜索CSDN内容
        
        Args:
            keyword: 搜索关键词
            page: 页码，从1开始
            scope: 搜索范围，默认为all
            
        Returns:
            Dict: 搜索结果
            
        Raises:
            CSDNAPIError: API调用失败时抛出
        """
        await self.init()
        
        try:
            logger.info(f"正在搜索... 关键词: {keyword}, 第{page}页")
            
            # 创建一个Future对象来存储响应
            response_future = asyncio.Future()
            
            def handle_response(response):
                asyncio.ensure_future(process_response(response))
                
            async def process_response(response):
                if 'so.csdn.net/api/v3/search' in response.url:
                    try:
                        json_data = await response.json()
                        if not response_future.done():
                            response_future.set_result(json_data)
                    except Exception as e:
                        logger.error(f"解析响应失败: {str(e)}")
                        try:
                            text = await response.text()
                            logger.error(f"响应内容: {text}")
                        except:
                            pass
                        if not response_future.done():
                            response_future.set_exception(e)
            
            # 监听响应
            self.page.on('response', handle_response)
            
            # 构建API URL
            api_url = f'https://so.csdn.net/api/v3/search?q={keyword}&t={scope}&p={page}&s=0&tm=0&lv=-1&ft=0&l=&u=&ct=-1&pnt=-1&ry=-1&ss=-1&dct=-1&vco=-1&cc=-1&sc=-1&akt=-1&art=-1&ca=-1&prs=&pre=&ecc=-1&ebc=-1&ia=1&platform=pc'
            
            # 访问搜索页面以触发API请求
            logger.info(f"访问搜索页面: {api_url}")
            await self.page.goto(f'https://so.csdn.net/so/search?q={keyword}&t={scope}&p={page}')
            await asyncio.sleep(2)  # 等待页面加载
            
            # 等待响应数据或超时
            try:
                response_data = await asyncio.wait_for(response_future, timeout=10.0)
                logger.info(f"搜索完成，获取到响应数据")
                return response_data
            except asyncio.TimeoutError:
                raise CSDNAPIError("搜索请求超时")
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            raise CSDNAPIError(f"搜索失败: {str(e)}") 
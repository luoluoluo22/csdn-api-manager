"""
CSDN API 异常类定义
"""

class CSDNError(Exception):
    """CSDN基础异常类"""
    pass

class CSDNAuthError(CSDNError):
    """认证相关异常"""
    pass

class CSDNAPIError(CSDNError):
    """API调用相关异常"""
    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class CSDNRateLimitError(CSDNError):
    """请求频率限制错误"""
    pass

class CSDNValidationError(CSDNError):
    """数据验证错误"""
    pass 
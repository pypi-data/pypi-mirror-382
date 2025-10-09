"""
Exception definition
"""


class XiangxinAIError(Exception):
    """Xiangxin AI guardrails base exception class"""
    pass


class AuthenticationError(XiangxinAIError):
    """Authentication error"""
    pass


class RateLimitError(XiangxinAIError):
    """Rate limit error"""
    pass


class ValidationError(XiangxinAIError):
    """Input validation error"""
    pass


class NetworkError(XiangxinAIError):
    """Network error"""
    pass


class ServerError(XiangxinAIError):
    """Server error"""
    pass
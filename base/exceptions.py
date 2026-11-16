"""
自定义异常：把 selenium 的底层异常包装成更容易理解的业务异常
便于在日志和测试报告里快速定位问题类型
"""


class BasePageError(Exception):
    """页面操作类异常的基类"""
    pass


class ElementNotFoundError(BasePageError):
    """元素在超时时间内没有找到"""
    pass


class ElementNotClickableError(BasePageError):
    """元素存在但无法点击（被遮挡、不可见）"""
    pass


class PageLoadError(BasePageError):
    """页面加载失败或跳转超时"""
    pass


class BusinessError(BasePageError):
    """业务校验失败，比如登录后没有跳转到首页"""
    pass

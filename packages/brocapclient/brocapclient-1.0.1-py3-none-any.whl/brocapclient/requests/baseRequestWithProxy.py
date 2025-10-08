from typing import Optional
from .baseRequest import BaseRequest
from .proxy_info import ProxyInfo

class BaseRequestWithProxy(BaseRequest):
    proxy: Optional[ProxyInfo] = None

from pydantic import Field
from typing import Dict, Union, Optional

from .baseRequestWithProxy import BaseRequestWithProxy

class HcaptchaRequest(BaseRequestWithProxy):
    type: str = Field(default='HCaptchaTask')
    websiteUrl: str
    websiteKey: str
    user_agent: str
    is_invisible: Optional[bool] = Field(default=None)
    data: Optional[str] = Field(default=None)
    cookies: Optional[str] = Field(default=None)
    fallbackToActualUA: Optional[bool] = Field(default=None)

    def getTaskDict(self) -> Dict[str, Union[str, int, bool]]:

        task = {}       
        task['type'] = self.type
        task['websiteURL'] = self.websiteUrl
        task['websiteKey'] = self.websiteKey
        task['userAgent'] = self.user_agent
        if self.proxy:
            task['proxyType'] = self.proxy.proxyType
            task['proxyAddress'] = self.proxy.proxyAddress
            task['proxyPort'] = self.proxy.proxyPort
            task['proxyLogin'] = self.proxy.proxyLogin
            task['proxyPassword'] = self.proxy.proxyPassword
        if self.is_invisible is not None:
            task['isInvisible'] = self.is_invisible
        if self.data is not None:
            task['data'] = self.data
        if self.cookies is not None:
            task['cookies'] = self.cookies
        if self.fallbackToActualUA is not None:
            task['fallbackToActualUA'] = self.fallbackToActualUA

        return task
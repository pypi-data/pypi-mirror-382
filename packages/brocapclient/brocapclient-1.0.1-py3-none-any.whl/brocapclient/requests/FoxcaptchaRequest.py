from typing import Dict, Union
from pydantic import Field

from .baseRequestWithProxy import BaseRequestWithProxy

class FoxcaptchaRequest(BaseRequestWithProxy):
    type: str = Field(default='CaptchaFoxTask')
    websiteUrl: str
    websiteKey: str
    userAgent: str
    
    def getTaskDict(self) -> Dict[str, Union[str, int, bool]]:
        task = {}
        task['type'] = self.type
        task['websiteURL'] = self.websiteUrl
        task['websiteKey'] = self.websiteKey
        task['userAgent'] = self.userAgent

        return task
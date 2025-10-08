from .baseRequest import BaseRequest
from .FoxcaptchaRequest import FoxcaptchaRequest
from .FuncaptchaRequest import FuncaptchaRequest
from .HcaptchaRequest import HcaptchaRequest
from .proxy_info import ProxyInfo

REQUESTS = [
    'FuncaptchaRequest', 'FunCaptchaComplexImageTaskRequest',
    'HcaptchaRequest', 'HcaptchaComplexImageTaskRequest'
]

from dataclasses import dataclass
from typing import Union


@dataclass
class GetResultTimeouts:
    firstRequestDelay: Union[int, float]
    firstRequestNoCacheDelay: Union[int, float]
    requestsInterval: Union[int, float] 
    timeout: Union[int, float]

def getFuncaptchaTimeouts() -> GetResultTimeouts:
    return GetResultTimeouts(1, 10, 1, 80)

def getHcaptchaTimeouts() -> GetResultTimeouts:
    return GetResultTimeouts(1, 10, 3, 180)

def getFoxcaptchaTimeouts() -> GetResultTimeouts:
    return GetResultTimeouts(1, 10, 3, 180)  # ???
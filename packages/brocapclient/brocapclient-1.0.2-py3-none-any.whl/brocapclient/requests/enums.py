from typing import List
from enum import Enum, unique


class BaseEnum(Enum):

    @classmethod
    def list_values(cls) -> List[str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_names(cls) -> List[str]:
        return list(map(lambda c: c.name, cls))

@unique
class ProxyTypes(BaseEnum):
    http_proxy = 'http'
    https_proxy = 'https'
    socks4_proxy = 'socks4'
    socks5_proxy = 'socks5'
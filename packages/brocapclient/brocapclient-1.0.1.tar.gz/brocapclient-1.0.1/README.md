## BroCapClient
Official python client library for [brocapgpt](https://docs.brocapgpt.com/) captcha recognition service

## Installation
```bash
python3 -m pip install brocapclient
```

## Usage
```python
import asyncio

from brocapclient.requests import HcaptchaRequest
from brocapclient import BroCapGptClient, ClientOptions

client_options = ClientOptions(api_key=<YOUR_API_KEY>)
brocap_client = BroCapGptClient(options=client_options)

async def solve_captcha(request):
    return await brocap_client.solve_captcha(request)

hcaptcha_request = HcaptchaRequest(
    websiteUrl='https://example.com/',
    websiteKey="d391ffb1-bc91-4ef8-a45a-2e2213af091b",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    fallbackToActualUA=True
)

responses = asyncio.run(solve_captcha(hcaptcha_request))
print(responses)
```

### Supported captcha recognition requests:
- [FunCaptcha](https://docs.brocapgpt.com/docs/captchas/funcaptcha-task/)
- [HCaptcha](https://docs.brocapgpt.com/docs/captchas/hcaptcha-task)
- [CaptchaFox](https://docs.brocapgpt.com/docs/captchas/captchafox-task)


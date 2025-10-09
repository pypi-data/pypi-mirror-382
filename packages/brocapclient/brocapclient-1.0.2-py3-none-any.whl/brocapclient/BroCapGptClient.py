import asyncio
from http.client import HTTPException
from typing import Dict, Union

import aiohttp

from .captchaResult import CaptchaResult
from .clientOptions import ClientOptions
from .exceptions import GetBalanceError, GetResultError, GetTaskError, UnknownRequestInstanceError
from .GetResultTimeouts import GetResultTimeouts, getFuncaptchaTimeouts, getHcaptchaTimeouts, getFoxcaptchaTimeouts
from .requestController import RequestController
from .requests import FuncaptchaRequest, HcaptchaRequest, FoxcaptchaRequest, BaseRequest, REQUESTS
from .utils import parseVersion

_instance_config = (
    ((FuncaptchaRequest,), getFuncaptchaTimeouts), 
    ((HcaptchaRequest,), getHcaptchaTimeouts),
    ((FoxcaptchaRequest,), getFoxcaptchaTimeouts)
)


class BroCapGptClient:
    def __init__(self, options: ClientOptions) -> None:
        self.options = options
        self._headers = {"User-Agent": f"BroCapGpt.Client.Python/{parseVersion()}"}

    @property
    def headers(self):
        return self._headers

    async def get_balance(self) -> Dict[str, Union[int, float, str]]:
        body = {"clientKey": self.options.api_key}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.options.service_url + "/getBalance",
                json=body,
                timeout=aiohttp.ClientTimeout(total=self.options.client_timeout),
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(f"Cannot create task. Status code: {resp.status}.")
                result = await resp.json(content_type=None)
                if result.get("errorId") != 0:
                    raise GetBalanceError(f"Cannot get balance on reason {result!s}")
                return result

    async def solve_captcha(
        self,
        request: Union[
            FuncaptchaRequest, HcaptchaRequest, FoxcaptchaRequest
        ],
    ) -> Dict[str, str]:
        """
        Non-blocking method for captcha solving.

        Args:
            request : This object must be an instance of "requests", otherwise an exception will be thrown
        """
        for instance_source, get_timeouts in _instance_config:
            if isinstance(request, instance_source):
                return await self._solve(request, get_timeouts())
        rs_all = "".join("\n" + x for x in REQUESTS)
        raise UnknownRequestInstanceError(
            f'Unknown request instance "{type(request)}", expected that request will belong next instances: {rs_all}'
        )

    async def _solve(
        self,
        request: Union[
            FuncaptchaRequest, HcaptchaRequest, FoxcaptchaRequest
        ],
        timeouts: GetResultTimeouts,
    ) -> Dict[str, str]:
        getTaskResponse = await self._createTask(request)
        if getTaskResponse.get("errorId") != 0:
            raise GetTaskError(f"[{getTaskResponse.get('errorCode')}] {getTaskResponse.get('errorDescription')}.")
        timer = RequestController(timeout=timeouts.timeout)
        await asyncio.sleep(timeouts.firstRequestDelay)
        result = CaptchaResult()
        while not timer.cancel:
            getResultResponse = await self._getTaskResult(getTaskResponse.get("taskId"))

            if getResultResponse.get("errorId") != 0:
                timer.stop()
                raise GetResultError(
                    f"[{getResultResponse.get('errorCode')}] {getResultResponse.get('errorDescription')}."
                )

            if getResultResponse.get("status") == "processing":
                await asyncio.sleep(timeouts.requestsInterval)
                continue

            elif getResultResponse.get("status") == "ready":
                timer.stop()
                result.solution = getResultResponse.get("solution")
                break

        if result != None:
            return result.solution
        else:
            raise TimeoutError(
                f"Failed to get a solution within the maximum response waiting interval: {timeouts.timeout:0.1f} sec."
            )

    async def _getTaskResult(self, task_id: str) -> Dict[str, Union[int, str, None]]:
        body = {"clientKey": self.options.api_key, "taskId": task_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.options.service_url + "/getTaskResult",
                json=body,
                timeout=aiohttp.ClientTimeout(total=self.options.client_timeout),
                headers=self.headers,
            ) as resp:
                if resp.status != 200:
                    if resp.status == 500:
                        return {"errorId": 0, "status": "processing"}
                    else:
                        raise HTTPException(f"Cannot grab result. Status code: {resp.status}.")
                else:
                    return await resp.json(content_type=None)

    async def _createTask(self, request: BaseRequest) -> Dict[str, Union[str, int]]:
        task = request.getTaskDict()
        body = {"clientKey": self.options.api_key, "task": task, "softId": self.options.default_soft_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.options.service_url + "/createTask",
                json=body,
                timeout=aiohttp.ClientTimeout(total=self.options.client_timeout),
                headers=self.headers,
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(f"Cannot create task. Status code: {resp.status}.")
                else:
                    return await resp.json(content_type=None)

import asyncio
from typing import Optional, Dict, Any, List
from llm_router.providers import ProviderRequest, ProviderResult, ProviderConnectionError

class FakeProvider:
    def __init__(
        self,
        name: str = "fake",
        status: int = 200,
        body: Optional[Dict[str, Any]] = None,
        delay: float = 0.0,
        exception: Optional[Exception] = None,
        retry_after_s: Optional[float] = None,
        ignore_cancel: bool = False
    ):
        self.name = name
        self.status = status
        self.body = body if body is not None else {
            "choices": [{"message": {"role": "assistant", "content": "hello"}}],
            "usage": {"total_tokens": 10}
        }
        self.delay = delay
        self.exception = exception
        self.retry_after_s = retry_after_s
        self.ignore_cancel = ignore_cancel
        self.call_count = 0
        self.cancelled = False
        self.calls: List[ProviderRequest] = []

    async def complete(self, request: ProviderRequest) -> ProviderResult:
        self.call_count += 1
        self.calls.append(request)
        if self.delay > 0:
            try:
                await asyncio.sleep(self.delay)
            except asyncio.CancelledError:
                self.cancelled = True
                if self.ignore_cancel:
                    await asyncio.sleep(0.5)
                raise

        if self.exception:
            raise self.exception

        return ProviderResult(
            status=self.status,
            body=self.body,
            retry_after_s=self.retry_after_s
        )

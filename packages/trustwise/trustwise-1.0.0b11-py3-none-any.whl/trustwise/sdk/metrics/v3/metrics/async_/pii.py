
from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import PIIMetricBase
from trustwise.sdk.types import PIIResponse


class PIIMetricAsync(PIIMetricBase):
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_safety_url("v3"), "pii")

    async def evaluate(self, *, text: str, blocklist: list[str] | None = None, allowlist: list[str] | None = None, **kwargs) -> PIIResponse:
        request_dict = self._build_request(text=text, allowlist=allowlist, blocklist=blocklist, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, texts: list[str], allowlist: list[str] | None = None, blocklist: list[str] | None = None) -> list[PIIResponse]:
        raise NotImplementedError("Batch evaluation not yet supported") 
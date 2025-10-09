from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    PIIRequestV4,
    PIIResponseV4,
)


class PIIMetricAsync(BaseMetric[PIIRequestV4, PIIResponseV4]):
    """PII metric async for v4 API."""
    response_type = PIIResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, allowlist: list[str] | None = None, blocklist: list[str] | None = None, categories: list[str] | None = None, **kwargs) -> dict:
        """Build the request dictionary for PII evaluation."""
        return self.validate_request_model(PIIRequestV4, text=text, allowlist=allowlist, blocklist=blocklist, categories=categories, **kwargs).to_dict()

    async def evaluate(self, *, text: str, allowlist: list[str] | None = None, blocklist: list[str] | None = None, categories: list[str] | None = None, **kwargs) -> PIIResponseV4:
        request_dict = self._build_request(text=text, allowlist=allowlist, blocklist=blocklist, categories=categories, **kwargs)
        result = await self.client.post(
            endpoint=f"{self.base_url}/pii",
            data=request_dict
        )
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[PIIResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

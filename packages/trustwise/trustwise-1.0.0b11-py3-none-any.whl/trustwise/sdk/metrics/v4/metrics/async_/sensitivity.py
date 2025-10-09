from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    SensitivityRequestV4,
    SensitivityResponseV4,
)


class SensitivityMetricAsync(BaseMetric[SensitivityRequestV4, SensitivityResponseV4]):
    """Sensitivity metric async for v4 API."""
    response_type = SensitivityResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, topics: list[str], **kwargs) -> dict:
        """Build the request dictionary for sensitivity evaluation."""
        return self.validate_request_model(SensitivityRequestV4, text=text, topics=topics, **kwargs).to_dict()

    async def evaluate(self, *, text: str, topics: list[str], **kwargs) -> SensitivityResponseV4:
        request_dict = self._build_request(text=text, topics=topics, **kwargs)
        result = await self.client.post(
            endpoint=f"{self.base_url}/sensitivity",
            data=request_dict
        )
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[SensitivityResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    StabilityRequestV4,
    StabilityResponseV4,
)


class StabilityMetricAsync(BaseMetric[StabilityRequestV4, StabilityResponseV4]):
    """Stability metric async for v4 API."""
    response_type = StabilityResponseV4

    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, responses: list[str], **kwargs) -> dict:
        """Build the request dictionary for stability evaluation."""
        return self.validate_request_model(StabilityRequestV4, responses=responses, **kwargs).to_dict()

    async def evaluate(self, *, responses: list[str], **kwargs) -> StabilityResponseV4:
        request_dict = self._build_request(responses=responses, **kwargs)
        endpoint = f"{self.base_url}/stability"
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

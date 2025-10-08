from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    AdherenceRequestV4,
    AdherenceResponseV4,
)


class AdherenceMetricAsync(BaseMetric[AdherenceRequestV4, AdherenceResponseV4]):
    """Adherence metric async for v4 API."""
    response_type = AdherenceResponseV4

    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, policy: str, response: str, **kwargs) -> dict:
        """Build the request dictionary for adherence evaluation."""
        return self.validate_request_model(AdherenceRequestV4, policy=policy, response=response, **kwargs).to_dict()

    async def evaluate(self, *, policy: str, response: str, **kwargs) -> AdherenceResponseV4:
        request_dict = self._build_request(policy=policy, response=response, **kwargs)
        endpoint = f"{self.base_url}/adherence"
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

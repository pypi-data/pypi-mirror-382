from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    RefusalRequestV4,
    RefusalResponseV4,
)


class RefusalMetricAsync(BaseMetric[RefusalRequestV4, RefusalResponseV4]):
    """Refusal metric async for v4 API."""
    response_type = RefusalResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, query: str, response: str, **kwargs) -> dict:
        """Build the request dictionary for refusal evaluation."""
        return self.validate_request_model(RefusalRequestV4, query=query, response=response, **kwargs).to_dict()

    async def evaluate(self, *, query: str, response: str, **kwargs) -> RefusalResponseV4:
        request_dict = self._build_request(query=query, response=response, **kwargs)
        result = await self.client.post(
            endpoint=f"{self.base_url}/refusal",
            data=request_dict
        )
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[RefusalResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

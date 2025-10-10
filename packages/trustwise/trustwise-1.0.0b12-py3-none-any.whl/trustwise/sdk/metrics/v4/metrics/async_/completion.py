from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    CompletionRequestV4,
    CompletionResponseV4,
)


class CompletionMetricAsync(BaseMetric[CompletionRequestV4, CompletionResponseV4]):
    """Completion metric async for v4 API."""
    response_type = CompletionResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, query: str, response: str, **kwargs) -> dict:
        """Build the request dictionary for completion evaluation."""
        return self.validate_request_model(CompletionRequestV4, query=query, response=response, **kwargs).to_dict()

    async def evaluate(self, *, query: str, response: str, **kwargs) -> CompletionResponseV4:
        request_dict = self._build_request(query=query, response=response, **kwargs)
        endpoint = f"{self.base_url}/completion"
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[CompletionResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

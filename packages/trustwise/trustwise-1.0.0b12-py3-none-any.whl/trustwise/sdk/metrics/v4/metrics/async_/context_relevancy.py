from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    ContextRelevancyRequestV4,
    ContextRelevancyResponseV4,
)


class ContextRelevancyMetricAsync(BaseMetric[ContextRelevancyRequestV4, ContextRelevancyResponseV4]):
    """Async context relevancy metric for v4 API."""
    response_type = ContextRelevancyResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, query: str, context: list, **kwargs) -> dict:
        """Build the request dictionary for context relevancy evaluation."""
        return self.validate_request_model(ContextRelevancyRequestV4, query=query, context=context, **kwargs).to_dict()

    async def evaluate(self, *, query: str, context: list, **kwargs) -> ContextRelevancyResponseV4:
        request_dict = self._build_request(query=query, context=context, **kwargs)
        result = await self.client.post(
            endpoint=f"{self.base_url}/context_relevancy",
            data=request_dict
        )
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[ContextRelevancyResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

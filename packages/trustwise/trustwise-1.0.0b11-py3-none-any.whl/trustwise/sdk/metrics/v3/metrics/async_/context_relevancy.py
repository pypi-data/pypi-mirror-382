from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import ContextRelevancyMetricBase
from trustwise.sdk.types import Context, ContextRelevancyResponse


class ContextRelevancyMetricAsync(ContextRelevancyMetricBase):
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_safety_url("v3"), "context_relevancy")

    async def evaluate(self, *, query: str | None = None, context: Context | None = None, **kwargs) -> ContextRelevancyResponse:
        request_dict = self._build_request(query=query, context=context, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result) 
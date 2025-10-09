from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import StabilityMetricBase
from trustwise.sdk.types import StabilityResponse


class StabilityMetricAsync(StabilityMetricBase):
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_metrics_url("v3"), "stability")

    async def evaluate(self, *, responses: list[str], **kwargs) -> StabilityResponse:
        request_dict = self._build_request(responses=responses, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[StabilityResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")

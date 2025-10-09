from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import CarbonMetricBase
from trustwise.sdk.types import CarbonResponse


class CarbonMetricAsync(CarbonMetricBase):
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_performance_url("v1"), "carbon")

    async def evaluate(self, *, processor_name: str | None = None, provider_name: str | None = None, provider_region: str | None = None, instance_type: str | None = None, average_latency: int | None = None, **kwargs) -> CarbonResponse:
        request_dict = self._build_request(processor_name, provider_name, provider_region, instance_type, average_latency, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list) -> list[CarbonResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import SensitivityMetricBase
from trustwise.sdk.types import SensitivityResponse


class SensitivityMetricAsync(SensitivityMetricBase):
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_alignment_url("v1"), "sensitivity")

    async def evaluate(self, *, response: str, topics: list, **kwargs) -> SensitivityResponse:
        request_dict = self._build_request(response=response, topics=topics, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list) -> list[SensitivityResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")

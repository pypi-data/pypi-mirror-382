from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import ToneMetricBase
from trustwise.sdk.types import ToneResponse


class ToneMetricAsync(ToneMetricBase):
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_alignment_url("v1"), "tone")

    async def evaluate(self, *, response: str | None = None, **kwargs) -> ToneResponse:
        request_dict = self._build_request(response, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list) -> list[ToneResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
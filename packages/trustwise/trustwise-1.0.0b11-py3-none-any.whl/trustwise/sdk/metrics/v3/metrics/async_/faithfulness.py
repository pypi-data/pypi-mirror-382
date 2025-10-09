from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import FaithfulnessMetricBase
from trustwise.sdk.types import Context, FaithfulnessResponse


class FaithfulnessMetricAsync(FaithfulnessMetricBase):
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_safety_url("v3"), "faithfulness")

    async def evaluate(self, *, query: str | None = None, response: str | None = None, context: Context | None = None, **kwargs) -> FaithfulnessResponse:
        request_dict = self._build_request(query=query, response=response, context=context, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[FaithfulnessResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
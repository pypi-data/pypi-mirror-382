from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import SummarizationMetricBase
from trustwise.sdk.types import Context, SummarizationResponse


class SummarizationMetricAsync(SummarizationMetricBase):
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_safety_url("v3"), "summarization")

    async def evaluate(self, *, response: str | None = None, context: Context | None = None, **kwargs) -> SummarizationResponse:
        request_dict = self._build_request(response=response, context=context, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[SummarizationResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")

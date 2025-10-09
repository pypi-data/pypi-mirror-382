from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import PromptInjectionMetricBase
from trustwise.sdk.types import PromptInjectionResponse


class PromptInjectionMetricAsync(PromptInjectionMetricBase):
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_safety_url("v3"), "prompt_injection")

    async def evaluate(self, *, query: str | None = None, **kwargs) -> PromptInjectionResponse:
        request_dict = self._build_request(query=query, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[PromptInjectionResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
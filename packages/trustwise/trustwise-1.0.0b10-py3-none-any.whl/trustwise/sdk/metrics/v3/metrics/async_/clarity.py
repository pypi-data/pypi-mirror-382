from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import ClarityMetricBase
from trustwise.sdk.types import ClarityResponse


class ClarityMetricAsync(ClarityMetricBase):
    """Async implementation of clarity metric."""
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_alignment_url("v1"), "clarity")

    async def evaluate(self, *, response: str | None = None, **kwargs) -> ClarityResponse:
        request_dict = self._build_request(response=response, **kwargs)
        result = await self.client.post(self._get_endpoint(), request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list) -> list[ClarityResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")

from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    ClarityRequestV4,
    ClarityResponseV4,
)


class ClarityMetricAsync(BaseMetric[ClarityRequestV4, ClarityResponseV4]):
    """Clarity metric async for v4 API."""
    response_type = ClarityResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, **kwargs) -> dict:
        """Build the request dictionary for clarity evaluation."""
        return self.validate_request_model(ClarityRequestV4, text=text, **kwargs).to_dict()

    async def evaluate(self, *, text: str, **kwargs) -> ClarityResponseV4:
        request_dict = self._build_request(text=text, **kwargs)
        result = await self.client.post(
            endpoint=f"{self.base_url}/clarity",
            data=request_dict
        )
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[ClarityResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    HelpfulnessRequestV4,
    HelpfulnessResponseV4,
)


class HelpfulnessMetricAsync(BaseMetric[HelpfulnessRequestV4, HelpfulnessResponseV4]):
    """Helpfulness metric async for v4 API."""
    response_type = HelpfulnessResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, **kwargs) -> dict:
        """Build the request dictionary for helpfulness evaluation."""
        return self.validate_request_model(HelpfulnessRequestV4, text=text, **kwargs).to_dict()

    async def evaluate(self, *, text: str, **kwargs) -> HelpfulnessResponseV4:
        request_dict = self._build_request(text=text, **kwargs)
        result = await self.client.post(
            endpoint=f"{self.base_url}/helpfulness",
            data=request_dict
        )
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[HelpfulnessResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    ToneRequestV4,
    ToneResponseV4,
)


class ToneMetricAsync(BaseMetric[ToneRequestV4, ToneResponseV4]):
    """Tone metric async for v4 API."""
    response_type = ToneResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, tones: list[str] | None = None, **kwargs) -> dict:
        """Build the request dictionary for tone evaluation."""
        return self.validate_request_model(ToneRequestV4, text=text, **kwargs).to_dict()

    async def evaluate(self, *, text: str, tones: list[str] | None = None, **kwargs) -> ToneResponseV4:
        request_dict = self._build_request(text=text, tones=tones, **kwargs)
        result = await self.client.post(
            endpoint=f"{self.base_url}/tone",
            data=request_dict
        )
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[ToneResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    ToneRequestV4,
    ToneResponseV4,
)


class ToneMetric(BaseMetric[ToneRequestV4, ToneResponseV4]):
    """Tone metric for v4 API."""
    response_type = ToneResponseV4
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, tones: list[str] | None = None, **kwargs) -> dict:
        """Build the request dictionary for tone evaluation."""
        return self.validate_request_model(ToneRequestV4, text=text, tones=tones, **kwargs).to_dict()

    def evaluate(self, *, text: str, tones: list[str] | None = None, **kwargs) -> ToneResponseV4:
        request_dict = self._build_request(text=text, tones=tones, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/tone",
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[ToneResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

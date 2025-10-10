from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    FormalityRequestV4,
    FormalityResponseV4,
)


class FormalityMetric(BaseMetric[FormalityRequestV4, FormalityResponseV4]):
    """Formality metric for v4 API."""
    response_type = FormalityResponseV4
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, **kwargs) -> dict:
        """Build the request dictionary for formality evaluation."""
        return self.validate_request_model(FormalityRequestV4, text=text, **kwargs).to_dict()

    def evaluate(self, *, text: str, **kwargs) -> FormalityResponseV4:
        request_dict = self._build_request(text=text, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/formality",
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[FormalityResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    SimplicityRequestV4,
    SimplicityResponseV4,
)


class SimplicityMetric(BaseMetric[SimplicityRequestV4, SimplicityResponseV4]):
    """Simplicity metric for v4 API."""
    response_type = SimplicityResponseV4
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, **kwargs) -> dict:
        """Build the request dictionary for simplicity evaluation."""
        return self.validate_request_model(SimplicityRequestV4, text=text, **kwargs).to_dict()

    def evaluate(self, *, text: str, **kwargs) -> SimplicityResponseV4:
        request_dict = self._build_request(text=text, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/simplicity",
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[SimplicityResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

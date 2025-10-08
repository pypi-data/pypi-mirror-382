from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    PIIRequestV4,
    PIIResponseV4,
)


class PIIMetric(BaseMetric[PIIRequestV4, PIIResponseV4]):
    """PII metric for v4 API."""
    response_type = PIIResponseV4
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, allowlist: list[str] | None = None, blocklist: list[str] | None = None, categories: list[str] | None = None, **kwargs) -> dict:
        """Build the request dictionary for PII evaluation."""
        return self.validate_request_model(PIIRequestV4, text=text, allowlist=allowlist, blocklist=blocklist, categories=categories, **kwargs).to_dict()

    def evaluate(self, *, text: str, allowlist: list[str] | None = None, blocklist: list[str] | None = None, categories: list[str] | None = None, **kwargs) -> PIIResponseV4:
        request_dict = self._build_request(text=text, allowlist=allowlist, blocklist=blocklist, categories=categories, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/pii",
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[PIIResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

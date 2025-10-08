from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    CompletionRequestV4,
    CompletionResponseV4,
)


class CompletionMetric(BaseMetric[CompletionRequestV4, CompletionResponseV4]):
    """Completion metric for v4 API."""
    response_type = CompletionResponseV4
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, query: str, response: str, **kwargs) -> dict:
        """Build the request dictionary for completion evaluation."""
        return self.validate_request_model(CompletionRequestV4, query=query, response=response, **kwargs).to_dict()

    def evaluate(self, *, query: str, response: str, **kwargs) -> CompletionResponseV4:
        request_dict = self._build_request(query=query, response=response, **kwargs)
        endpoint = f"{self.base_url}/completion"
        result = self.client._post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[CompletionResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import ClarityMetricBase
from trustwise.sdk.types import ClarityResponse


class ClarityMetric(ClarityMetricBase):
    """Sync implementation of clarity metric."""
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_alignment_url("v1"), "clarity")

    def evaluate(self, *, response: str | None = None, **kwargs) -> ClarityResponse:
        request_dict = self._build_request(response=response, **kwargs)
        result = self.client._post(self._get_endpoint(), request_dict)
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list) -> list[ClarityResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
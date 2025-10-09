from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import StabilityMetricBase
from trustwise.sdk.types import StabilityResponse


class StabilityMetric(StabilityMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_metrics_url("v3"), "stability")

    def evaluate(self, *, responses: list[str], **kwargs) -> StabilityResponse:
        request_dict = self._build_request(responses=responses, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[StabilityResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")

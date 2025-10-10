from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import AdherenceMetricBase
from trustwise.sdk.types import AdherenceResponse


class AdherenceMetric(AdherenceMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_metrics_url("v3"), "adherence")

    def evaluate(self, *, policy: str, response: str, **kwargs) -> AdherenceResponse:
        request_dict = self._build_request(policy=policy, response=response, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[AdherenceResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")

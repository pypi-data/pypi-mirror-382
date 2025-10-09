from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import RefusalMetricBase
from trustwise.sdk.types import RefusalResponse


class RefusalMetric(RefusalMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_metrics_url("v3"), "refusal")

    def evaluate(self, *, query: str, response: str, **kwargs) -> RefusalResponse:
        request_dict = self._build_request(query=query, response=response, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[RefusalResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")


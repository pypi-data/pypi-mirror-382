from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import CompletionMetricBase
from trustwise.sdk.types import CompletionResponse


class CompletionMetric(CompletionMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_metrics_url("v3"), "completion")

    def evaluate(self, *, query: str, response: str, **kwargs) -> CompletionResponse:
        request_dict = self._build_request(query=query, response=response, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[CompletionResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")

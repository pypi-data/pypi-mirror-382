from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import SummarizationMetricBase
from trustwise.sdk.types import Context, SummarizationResponse


class SummarizationMetric(SummarizationMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_safety_url("v3"), "summarization")

    def evaluate(self, *, response: str | None = None, context: Context | None = None, **kwargs) -> SummarizationResponse:
        request_dict = self._build_request(response=response, context=context, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[SummarizationResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")

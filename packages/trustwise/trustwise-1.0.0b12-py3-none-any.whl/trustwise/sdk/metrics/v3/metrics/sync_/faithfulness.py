from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import FaithfulnessMetricBase
from trustwise.sdk.types import Context, FaithfulnessResponse


class FaithfulnessMetric(FaithfulnessMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_safety_url("v3"), "faithfulness")

    def evaluate(self, *, query: str | None = None, response: str | None = None, context: Context | None = None, **kwargs) -> FaithfulnessResponse:
        request_dict = self._build_request(query=query, response=response, context=context, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[FaithfulnessResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
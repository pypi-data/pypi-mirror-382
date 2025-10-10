from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import ToxicityMetricBase
from trustwise.sdk.types import ToxicityResponse


class ToxicityMetric(ToxicityMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_alignment_url("v1"), "toxicity")

    def evaluate(self, *, response: str | None = None, **kwargs) -> ToxicityResponse:
        request_dict = self._build_request(response, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(
            endpoint=endpoint,
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list) -> list[ToxicityResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
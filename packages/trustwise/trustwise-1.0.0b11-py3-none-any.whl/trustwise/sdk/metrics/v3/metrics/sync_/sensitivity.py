from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import SensitivityMetricBase
from trustwise.sdk.types import SensitivityResponse


class SensitivityMetric(SensitivityMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_alignment_url("v1"), "sensitivity")

    def evaluate(self, *, response: str | None = None, topics: list | None = None, **kwargs) -> SensitivityResponse:
        request_dict = self._build_request(response, topics, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(
            endpoint=endpoint,
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list) -> list[SensitivityResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
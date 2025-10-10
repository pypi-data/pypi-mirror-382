from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import SimplicityMetricBase
from trustwise.sdk.types import SimplicityResponse


class SimplicityMetric(SimplicityMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_alignment_url("v1"), "simplicity")

    def evaluate(self, *, response: str | None = None, **kwargs) -> SimplicityResponse:
        request_dict = self._build_request(response, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(
            endpoint=endpoint,
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list) -> list[SimplicityResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
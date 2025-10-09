from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import PromptInjectionMetricBase
from trustwise.sdk.types import PromptInjectionResponse


class PromptInjectionMetric(PromptInjectionMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_safety_url("v3")

    def evaluate(self, *, query: str | None = None, **kwargs) -> PromptInjectionResponse:
        request_dict = self._build_request(query=query, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/prompt_injection",
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[PromptInjectionResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
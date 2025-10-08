from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    PromptManipulationRequestV4,
    PromptManipulationResponseV4,
)


class PromptManipulationMetric(BaseMetric[PromptManipulationRequestV4, PromptManipulationResponseV4]):
    """Prompt manipulation metric for v4 API."""
    response_type = PromptManipulationResponseV4
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, severity: int | None = None, **kwargs) -> dict:
        """Build the request dictionary for prompt manipulation evaluation."""
        return self.validate_request_model(PromptManipulationRequestV4, text=text, severity=severity, **kwargs).to_dict()

    def evaluate(self, *, text: str, severity: int | None = None, **kwargs) -> PromptManipulationResponseV4:
        request_dict = self._build_request(text=text, severity=severity, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/prompt_manipulation",
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[PromptManipulationResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

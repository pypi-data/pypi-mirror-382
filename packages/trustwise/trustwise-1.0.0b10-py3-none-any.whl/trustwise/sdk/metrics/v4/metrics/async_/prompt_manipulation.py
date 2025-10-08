from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    PromptManipulationRequestV4,
    PromptManipulationResponseV4,
)


class PromptManipulationMetricAsync(BaseMetric[PromptManipulationRequestV4, PromptManipulationResponseV4]):
    """Async prompt manipulation metric for v4 API."""
    response_type = PromptManipulationResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, text: str, severity: int | None = None, **kwargs) -> dict:
        """Build the request dictionary for prompt manipulation evaluation."""
        return self.validate_request_model(PromptManipulationRequestV4, text=text, severity=severity, **kwargs).to_dict()

    async def evaluate(self, *, text: str, severity: int = 1, **kwargs) -> PromptManipulationResponseV4:
        request_dict = self._build_request(text=text, severity=severity, **kwargs)
        result = await self.client.post(
            endpoint=f"{self.base_url}/prompt_manipulation",
            data=request_dict
        )
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[PromptManipulationResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

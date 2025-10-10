from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    FaithfulnessRequestV4,
    FaithfulnessResponseV4,
)


class FaithfulnessMetricAsync(BaseMetric[FaithfulnessRequestV4, FaithfulnessResponseV4]):
    """Faithfulness metric async for v4 API."""
    response_type = FaithfulnessResponseV4
    
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, query: str, response: str, context: list, *, severity: float | None = None, include_citations: bool | None = None, **kwargs) -> dict:
        """Build the request dictionary for faithfulness evaluation."""
        return self.validate_request_model(FaithfulnessRequestV4, query=query, response=response, context=context, severity=severity, include_citations=include_citations, **kwargs).to_dict()

    async def evaluate(self, *, query: str, response: str, context: list, severity: float | None = None, include_citations: bool | None = None, **kwargs) -> FaithfulnessResponseV4:
        request_dict = self._build_request(query=query, response=response, context=context, severity=severity, include_citations=include_citations, **kwargs)
        result = await self.client.post(
            endpoint=f"{self.base_url}/faithfulness",
            data=request_dict
        )
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[FaithfulnessResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

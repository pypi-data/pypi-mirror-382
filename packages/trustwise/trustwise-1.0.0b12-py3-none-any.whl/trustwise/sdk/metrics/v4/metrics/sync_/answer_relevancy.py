from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import BaseMetric
from trustwise.sdk.metrics.v4.types import (
    AnswerRelevancyRequestV4,
    AnswerRelevancyResponseV4,
)


class AnswerRelevancyMetric(BaseMetric[AnswerRelevancyRequestV4, AnswerRelevancyResponseV4]):
    """Answer relevancy metric for v4 API."""
    response_type = AnswerRelevancyResponseV4
    
    def __init__(self, client: TrustwiseClient) -> None:
        self.client = client
        self.base_url = client.config.get_metrics_url("v4alpha")

    def _build_request(self, query: str, response: str, **kwargs) -> dict:
        """Build the request dictionary for answer relevancy evaluation."""
        return self.validate_request_model(AnswerRelevancyRequestV4, query=query, response=response, **kwargs).to_dict()

    def evaluate(self, *, query: str, response: str, **kwargs) -> AnswerRelevancyResponseV4:
        request_dict = self._build_request(query=query, response=response, **kwargs)
        result = self.client._post(
            endpoint=f"{self.base_url}/answer_relevancy",
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list[dict]) -> list[AnswerRelevancyResponseV4]:
        raise NotImplementedError("Batch evaluation not yet supported")

from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.metrics.base import AnswerRelevancyMetricBase
from trustwise.sdk.types import AnswerRelevancyResponse


class AnswerRelevancyMetricAsync(AnswerRelevancyMetricBase):
    """
    Concrete implementation of AnswerRelevancyMetricBase for async clients.
    """

    def __init__(self, client: TrustwiseAsyncClient) -> None:
        super().__init__(client, client.config.get_safety_url("v3"), "answer_relevancy")

    async def evaluate(self, *, query: str | None = None, response: str | None = None, **kwargs) -> AnswerRelevancyResponse:
        request_dict = self._build_request(query=query, response=response, **kwargs)
        endpoint = self._get_endpoint()
        result = await self.client.post(endpoint=endpoint, data=request_dict)
        return self._parse_response(result)

    async def batch_evaluate(self, inputs: list[dict]) -> list[AnswerRelevancyResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
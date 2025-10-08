from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import CostMetricBase
from trustwise.sdk.types import CostResponse


class CostMetric(CostMetricBase):
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_performance_url("v1"), "cost")

    def evaluate(self, *, model_name: str | None = None, model_type: str | None = None, model_provider: str | None = None, number_of_queries: int | None = None, total_prompt_tokens: int | None = None, total_completion_tokens: int | None = None, total_tokens: int | None = None, instance_type: str | None = None, average_latency: float | None = None, **kwargs) -> CostResponse:
        request_dict = self._build_request(
            model_name=model_name,
            model_type=model_type,
            model_provider=model_provider,
            number_of_queries=number_of_queries,
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            total_tokens=total_tokens,
            instance_type=instance_type,
            average_latency=average_latency,
            **kwargs
        )
        endpoint = self._get_endpoint()
        result = self.client._post(
            endpoint=endpoint,
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list) -> list[CostResponse]:
        raise NotImplementedError("Batch evaluation not yet supported")
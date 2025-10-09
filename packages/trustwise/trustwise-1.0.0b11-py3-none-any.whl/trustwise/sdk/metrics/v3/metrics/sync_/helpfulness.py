from trustwise.sdk.client import TrustwiseClient
from trustwise.sdk.metrics.base import HelpfulnessMetricBase
from trustwise.sdk.types import HelpfulnessResponse


class HelpfulnessMetric(HelpfulnessMetricBase):
    """Helpfulness metric for evaluating response helpfulness."""
    def __init__(self, client: TrustwiseClient) -> None:
        super().__init__(client, client.config.get_alignment_url("v1"), "helpfulness")

    def evaluate(
        self,
        *,
        response: str | None = None,
        **kwargs
    ) -> HelpfulnessResponse:
        """
        Evaluate the helpfulness of a response.

        Args:
            response: The response string (required)

        Returns:
            HelpfulnessResponse containing the evaluation results
        """
        request_dict = self._build_request(response, **kwargs)
        endpoint = self._get_endpoint()
        result = self.client._post(
            endpoint=endpoint,
            data=request_dict
        )
        return self._parse_response(result)

    def batch_evaluate(self, inputs: list) -> list[HelpfulnessResponse]:
        """Evaluate multiple inputs for helpfulness."""
        raise NotImplementedError("Batch evaluation not yet supported")
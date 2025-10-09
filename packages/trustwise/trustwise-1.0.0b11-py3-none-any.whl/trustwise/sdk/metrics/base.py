import logging
import warnings
from abc import ABC, abstractmethod
from typing import (
    Any,
    Generic,
    TypeVar,
)

from pydantic import ValidationError

from trustwise.sdk.exceptions import TrustwiseValidationError
from trustwise.sdk.types import (
    AdherenceRequest,
    AdherenceResponse,
    AnswerRelevancyRequest,
    AnswerRelevancyResponse,
    CarbonRequest,
    CarbonResponse,
    ClarityRequest,
    ClarityResponse,
    CompletionRequest,
    CompletionResponse,
    ContextRelevancyRequest,
    ContextRelevancyResponse,
    CostRequest,
    CostResponse,
    FaithfulnessRequest,
    FaithfulnessResponse,
    FormalityRequest,
    FormalityResponse,
    HelpfulnessRequest,
    HelpfulnessResponse,
    PIIRequest,
    PIIResponse,
    PromptInjectionRequest,
    PromptInjectionResponse,
    RefusalRequest,
    RefusalResponse,
    SDKBaseModel,
    SensitivityRequest,
    SensitivityResponse,
    SimplicityRequest,
    SimplicityResponse,
    StabilityRequest,
    StabilityResponse,
    SummarizationRequest,
    SummarizationResponse,
    ToneRequest,
    ToneResponse,
    ToxicityRequest,
    ToxicityResponse,
)

logger = logging.getLogger(__name__)

# Generic type variables for request and response
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


class BaseMetric(ABC, Generic[TRequest, TResponse]):  # noqa: UP046
    """
    Base class for all metrics. Each metric should inherit from this class
    and implement the required methods.
    """
    response_type = None  # Subclasses must set this
    
    def __init__(self, client: Any, base_url: str, endpoint: str) -> None:
        """
        Initialize a metric.
        
        Args:
            client: The client instance (sync or async)
            base_url: Base URL for the API
            endpoint: The specific endpoint for this metric
        """
        self.client = client
        self.base_url = base_url
        self.endpoint = endpoint
        logger.debug("Initialized %s with base_url: %s, endpoint: %s", 
                    self.__class__.__name__, base_url, endpoint)

    def _get_endpoint(self) -> str:
        """Get the full URL for this metric's endpoint."""
        return f"{self.base_url}/{self.endpoint}"

    def _check_deprecation(self) -> None:
        """Check if this metric is deprecated and emit a warning if so."""
        # Check if this is a v3 metric by looking at the base_url
        if "v3" in self.base_url:
            warnings.warn(
                "V3 metrics are deprecated and will be removed in a future version. "
                "Please migrate to V4 metrics for continued support and enhanced features. "
                "See the migration guide for more details: https://trustwiseai.github.io/tw-docs/docs/migration_guide",
                FutureWarning,
                stacklevel=3
            )

    @abstractmethod
    def evaluate(self, *args: Any, **kwargs: Any) -> Any:
        """Evaluate the metric. Must be implemented by concrete classes."""
        raise NotImplementedError

    @abstractmethod
    def _build_request(self, *args, **kwargs) -> dict:
        """Build the request dictionary. Must be implemented by concrete classes."""
        raise NotImplementedError
    
    @staticmethod
    def _handle_new_api_response(result: dict) -> tuple[dict, dict | None]:
        """
        Handle the new API response format with data wrapper.
        Returns a tuple of (data, metadata).
        """
        data = result["data"]
        metadata = result.get("metadata", None)
        if "message" in result:
            logger.debug("API response message: %s", result["message"])
        return data, metadata

    def _parse_response(self, result: dict) -> TResponse:
        """
        Parse the response using the metric's response type.
        Attaches metadata as _metadata attribute if present.
        
        Returns:
            The parsed response object with _metadata attribute if metadata exists.
        """
        logger.debug("Parsing response for %s", self.response_type.__name__)
        if self.response_type is None:
            raise NotImplementedError("Subclasses must set response_type")

        # Handle new API response format with data wrapper
        if "data" in result and isinstance(result["data"], dict):
            data, metadata = self._handle_new_api_response(result)
        else:
            # Handle legacy direct response format
            data = result
            metadata = result.get("metadata", None)
        
        original_response = result

        try:
            parsed_data = self.response_type(**data)
            
            # Attach metadata as _metadata attribute if it exists
            # Using underscore prefix to clearly indicate this is API-level metadata
            # not part of the evaluation result data
            if metadata is not None:
                parsed_data._metadata = metadata
            
            return parsed_data
            
        except Exception as e:
            # Log additional context for better debugging
            if original_response != data:
                # Wrapped response format - log both original and extracted data
                logger.error(
                    "Failed to parse %s from wrapped response. "
                    "Original response: %s, Extracted data: %s, Error: %s",
                    self.response_type.__name__, original_response, data, e
                )
            else:
                # Direct response format
                logger.error(
                    "Failed to parse %s from response: %s, Error: %s",
                    self.response_type.__name__, data, e
                )
            # Re-raise the original exception to preserve Pydantic validation details
            raise

    def batch_evaluate(self, inputs: list[TRequest]) -> list[TResponse]:
        """Evaluate multiple inputs in a single request. Optional implementation."""
        raise NotImplementedError("Batch evaluation not supported for this metric")

    @staticmethod
    def validate_request_model(model_cls: type, **kwargs: Any) -> object:
        """
        Standardized Trustwise validation for all metric request models.
        Usage: req = BaseMetric.validate_request_model(RequestModel, **kwargs)
        Raises TrustwiseValidationError with a formatted message on error.
        """
        try:
            return model_cls(**kwargs)
        except ValidationError as ve:
            raise TrustwiseValidationError(SDKBaseModel.format_validation_error(model_cls, ve)) from ve
        except TypeError as te:
            # Detect missing required arguments
            import inspect
            sig = inspect.signature(model_cls)
            missing_args = []
            for name, param in sig.parameters.items():
                if param.default is param.empty and name not in kwargs:
                    missing_args.append(name)
            if missing_args:
                class DummyValidationError(Exception):
                    def errors(self) -> list:
                        return [
                            {"loc": [arg], "msg": "field required"} for arg in missing_args
                        ]
                ve = DummyValidationError()
                raise TrustwiseValidationError(SDKBaseModel.format_validation_error(model_cls, ve)) from te
            else:
                raise


# Rest of the metric base classes remain unchanged
class ClarityMetricBase(BaseMetric[ClarityRequest, ClarityResponse]):
    """Base class for clarity metric implementations."""
    response_type = ClarityResponse
    
    def _build_request(self, response: str, **kwargs) -> dict:
        """Build the request dictionary for clarity evaluation."""
        return self.validate_request_model(ClarityRequest, response=response, **kwargs).to_dict()


class HelpfulnessMetricBase(BaseMetric[HelpfulnessRequest, HelpfulnessResponse]):
    """Base class for helpfulness metric implementations."""
    response_type = HelpfulnessResponse
    
    def _build_request(self, response: str, **kwargs) -> dict:
        """Build the request dictionary for helpfulness evaluation."""
        return self.validate_request_model(HelpfulnessRequest, response=response, **kwargs).to_dict()


class FormalityMetricBase(BaseMetric[FormalityRequest, FormalityResponse]):
    """Base class for formality metric implementations."""
    response_type = FormalityResponse
    
    def _build_request(self, response: str, **kwargs) -> dict:
        """Build the request dictionary for formality evaluation."""
        return self.validate_request_model(FormalityRequest, response=response, **kwargs).to_dict()


class SimplicityMetricBase(BaseMetric[SimplicityRequest, SimplicityResponse]):
    """Base class for simplicity metric implementations."""
    response_type = SimplicityResponse
    
    def _build_request(self, response: str, **kwargs) -> dict:
        """Build the request dictionary for simplicity evaluation."""
        return self.validate_request_model(SimplicityRequest, response=response, **kwargs).to_dict()


class SensitivityMetricBase(BaseMetric[SensitivityRequest, SensitivityResponse]):
    """Base class for sensitivity metric implementations."""
    response_type = SensitivityResponse
    
    def _build_request(self, response: str, topics: list[str] | None = None, **kwargs) -> dict:
        """Build the request dictionary for sensitivity evaluation."""
        return self.validate_request_model(SensitivityRequest, response=response, topics=topics, **kwargs).to_dict()


class ToneMetricBase(BaseMetric[ToneRequest, ToneResponse]):
    """Base class for tone metric implementations."""
    response_type = ToneResponse
    
    def _build_request(self, response: str, **kwargs) -> dict:
        """Build the request dictionary for tone evaluation."""
        return self.validate_request_model(ToneRequest, response=response, **kwargs).to_dict()


class FaithfulnessMetricBase(BaseMetric[FaithfulnessRequest, FaithfulnessResponse]):
    """Base class for faithfulness metric implementations."""
    response_type = FaithfulnessResponse
    
    def _build_request(self, query: str, response: str, context: list, **kwargs) -> dict:
        """Build the request dictionary for faithfulness evaluation."""
        return self.validate_request_model(FaithfulnessRequest, query=query, response=response, context=context, **kwargs).to_dict()


class CarbonMetricBase(BaseMetric[CarbonRequest, CarbonResponse]):
    """Base class for carbon metric implementations."""
    response_type = CarbonResponse
    
    def _build_request(self, processor_name: str, provider_name: str, provider_region: str, 
                      instance_type: str, average_latency: int, **kwargs) -> dict:
        """Build the request dictionary for carbon evaluation."""
        return self.validate_request_model(
            CarbonRequest,
            processor_name=processor_name,
            provider_name=provider_name,
            provider_region=provider_region,
            instance_type=instance_type,
            average_latency=average_latency,
            **kwargs
        ).to_dict()


class CostMetricBase(BaseMetric[CostRequest, CostResponse]):
    """Base class for cost metric implementations."""
    response_type = CostResponse
    
    def _build_request(self, model_name: str, model_type: str, model_provider: str,
                      number_of_queries: int, total_prompt_tokens: int,
                      total_completion_tokens: int, **kwargs) -> dict:
        """Build the request dictionary for cost evaluation."""
        return self.validate_request_model(
            CostRequest,
            model_name=model_name,
            model_type=model_type,
            model_provider=model_provider,
            number_of_queries=number_of_queries,
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            **kwargs
        ).to_dict()


class ContextRelevancyMetricBase(BaseMetric[ContextRelevancyRequest, ContextRelevancyResponse]):
    """Base class for context relevancy metric implementations."""
    response_type = ContextRelevancyResponse
    
    def _build_request(self, query: str, context: list, **kwargs) -> dict:
        """Build the request dictionary for context relevancy evaluation."""
        request_dict = self.validate_request_model(ContextRelevancyRequest, query=query, context=context, **kwargs).to_dict()
        request_dict["response"] = "placeholder" # TODO: Remove this once the API is updated
        return request_dict


class SummarizationMetricBase(BaseMetric[SummarizationRequest, SummarizationResponse]):
    """Base class for summarization metric implementations."""
    response_type = SummarizationResponse
    
    def _build_request(self, response: str, context: list, **kwargs) -> dict:
        """Build the request dictionary for summarization evaluation."""
        request_dict = self.validate_request_model(SummarizationRequest, response=response, context=context, **kwargs).to_dict()
        request_dict["query"] = "placeholder" # TODO: Remove this once the API is updated
        return request_dict


class AnswerRelevancyMetricBase(BaseMetric[AnswerRelevancyRequest, AnswerRelevancyResponse]):
    """Base class for answer relevancy metric implementations."""
    response_type = AnswerRelevancyResponse
    
    def _build_request(self, *args, **kwargs) -> dict:
        req = self.validate_request_model(AnswerRelevancyRequest, *args, **kwargs)
        request_dict = req.to_dict()
        request_dict["context"] = [{"node_id": "0", "node_score": 0, "node_text": "placeholder"}]  # TODO: Remove this once the API is updated
        return request_dict


class PIIMetricBase(BaseMetric[PIIRequest, PIIResponse]):
    """Base class for PII metric implementations."""
    response_type = PIIResponse
    
    def _build_request(self, text: str, allowlist: list[str], blocklist: list[str], **kwargs) -> dict:
        """Build the request dictionary for PII evaluation."""
        return self.validate_request_model(PIIRequest, text=text, allowlist=allowlist, blocklist=blocklist, **kwargs).to_dict()


class PromptInjectionMetricBase(BaseMetric[PromptInjectionRequest, PromptInjectionResponse]):
    """Base class for prompt injection metric implementations."""
    response_type = PromptInjectionResponse
    
    def _build_request(self, query: str, **kwargs) -> dict:
        """Build the request dictionary for prompt injection evaluation."""
        request_dict = self.validate_request_model(PromptInjectionRequest, query=query, **kwargs).to_dict()
        request_dict["context"] = [{"node_id": "0", "node_score": 0, "node_text": "placeholder"}] # TODO: Remove this once the API is updated
        request_dict["response"] = "placeholder" # TODO: Remove this once the API is updated
        return request_dict


class ToxicityMetricBase(BaseMetric[ToxicityRequest, ToxicityResponse]):
    """Base class for toxicity metric implementations."""
    response_type = ToxicityResponse
    
    def _build_request(self, response: str, **kwargs) -> dict:
        """Build the request dictionary for toxicity evaluation."""
        return self.validate_request_model(ToxicityRequest, response=response, **kwargs).to_dict()


class RefusalMetricBase(BaseMetric[RefusalRequest, RefusalResponse]):
    """Base class for refusal metric implementations."""
    response_type = RefusalResponse
    
    def _build_request(self, query: str, response: str, **kwargs) -> dict:
        """Build the request dictionary for refusal evaluation."""
        return self.validate_request_model(RefusalRequest, query=query, response=response, **kwargs).to_dict()


class StabilityMetricBase(BaseMetric[StabilityRequest, StabilityResponse]):
    """Base class for stability metric implementations."""
    response_type = StabilityResponse
    
    def _build_request(self, responses: list[str], **kwargs) -> dict:
        """Build the request dictionary for stability evaluation."""
        return self.validate_request_model(StabilityRequest, responses=responses, **kwargs).to_dict()


class CompletionMetricBase(BaseMetric[CompletionRequest, CompletionResponse]):
    """Base class for completion metric implementations."""
    response_type = CompletionResponse
    
    def _build_request(self, query: str, response: str, **kwargs) -> dict:
        """Build the request dictionary for completion evaluation."""
        return self.validate_request_model(CompletionRequest, query=query, response=response, **kwargs).to_dict()


class AdherenceMetricBase(BaseMetric[AdherenceRequest, AdherenceResponse]):
    """Base class for adherence metric implementations."""
    response_type = AdherenceResponse
    
    def _build_request(self, policy: str, response: str, **kwargs) -> dict:
        """Build the request dictionary for adherence evaluation."""
        return self.validate_request_model(AdherenceRequest, policy=policy, response=response, **kwargs).to_dict()

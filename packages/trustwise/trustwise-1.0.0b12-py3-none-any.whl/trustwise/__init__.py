"""Trustwise SDK for evaluating AI-generated content."""

try:
    from importlib.metadata import version
    __version__ = version("trustwise")
except ImportError:
    # Fallback for Python < 3.8
    from pkg_resources import get_distribution
    __version__ = get_distribution("trustwise").version

# Export exceptions using absolute imports
from trustwise.sdk.exceptions import (
    TrustwiseAPIError,
    TrustwiseSDKError,
    TrustwiseValidationError,
)

# Export types for type checking and user convenience
from trustwise.sdk.types import (
    AnswerRelevancyRequest,
    AnswerRelevancyResponse,
    CarbonRequest,
    CarbonResponse,
    ClarityRequest,
    ClarityResponse,
    Context,
    ContextNode,
    ContextRelevancyRequest,
    ContextRelevancyResponse,
    CostRequest,
    CostResponse,
    Fact,
    Facts,
    FaithfulnessRequest,
    FaithfulnessResponse,
    FormalityRequest,
    FormalityResponse,
    GuardrailResponse,
    HelpfulnessRequest,
    HelpfulnessResponse,
    PIIEntity,
    PIIRequest,
    PIIResponse,
    PromptInjectionRequest,
    PromptInjectionResponse,
    SensitivityRequest,
    SensitivityResponse,
    SimplicityRequest,
    SimplicityResponse,
    SummarizationRequest,
    SummarizationResponse,
    ToneRequest,
    ToneResponse,
    ToxicityRequest,
    ToxicityResponse,
)

__all__ = [
    "AnswerRelevancyRequest",
    "AnswerRelevancyResponse",
    "CarbonRequest",
    "CarbonResponse",
    "ClarityRequest",
    "ClarityResponse",
    "Context",
    "ContextNode",
    "ContextRelevancyRequest",
    "ContextRelevancyResponse",
    "CostRequest",
    "CostResponse",
    "Fact",
    "Facts",
    "FaithfulnessRequest",
    "FaithfulnessResponse",
    "FormalityRequest",
    "FormalityResponse",
    "GuardrailResponse",
    "HelpfulnessRequest",
    "HelpfulnessResponse",
    "PIIEntity",
    "PIIRequest",
    "PIIResponse",
    "PromptInjectionRequest",
    "PromptInjectionResponse",
    "SensitivityRequest",
    "SensitivityResponse",
    "SimplicityRequest",
    "SimplicityResponse",
    "SummarizationRequest",
    "SummarizationResponse",
    "ToneRequest",
    "ToneResponse",
    "ToxicityRequest",
    "ToxicityResponse",
    "TrustwiseAPIError",
    "TrustwiseSDKError",
    "TrustwiseValidationError",
]

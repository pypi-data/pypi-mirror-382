import logging
import warnings
from typing import Any

from trustwise.sdk.async_client import TrustwiseAsyncClient
from trustwise.sdk.config import TrustwiseConfig
from trustwise.sdk.metrics.v3.metrics.async_ import (
    AdherenceMetricAsync,
    AnswerRelevancyMetricAsync,
    CarbonMetricAsync,
    ClarityMetricAsync,
    CompletionMetricAsync,
    ContextRelevancyMetricAsync,
    CostMetricAsync,
    FaithfulnessMetricAsync,
    FormalityMetricAsync,
    HelpfulnessMetricAsync,
    PIIMetricAsync,
    PromptInjectionMetricAsync,
    RefusalMetricAsync,
    SensitivityMetricAsync,
    SimplicityMetricAsync,
    StabilityMetricAsync,
    SummarizationMetricAsync,
    ToneMetricAsync,
    ToxicityMetricAsync,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    AdherenceMetricAsync as AdherenceMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    AnswerRelevancyMetricAsync as AnswerRelevancyMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    ClarityMetricAsync as ClarityMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    CompletionMetricAsync as CompletionMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    ContextRelevancyMetricAsync as ContextRelevancyMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    FaithfulnessMetricAsync as FaithfulnessMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    FormalityMetricAsync as FormalityMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    HelpfulnessMetricAsync as HelpfulnessMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    PIIMetricAsync as PIIMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    PromptManipulationMetricAsync as PromptManipulationMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    RefusalMetricAsync as RefusalMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    SensitivityMetricAsync as SensitivityMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    SimplicityMetricAsync as SimplicityMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    StabilityMetricAsync as StabilityMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    ToneMetricAsync as ToneMetricAsyncV4,
)
from trustwise.sdk.metrics.v4.metrics.async_ import (
    ToxicityMetricAsync as ToxicityMetricAsyncV4,
)

logger = logging.getLogger(__name__)

class DeprecatedMetricWrapperAsync:
    """Wrapper class that adds deprecation warnings to v3 async metrics."""
    
    def __init__(self, metric_instance: Any) -> None:
        self._metric = metric_instance
        
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the wrapped metric."""
        return getattr(self._metric, name)
    
    async def evaluate(self, *args: Any, **kwargs: Any) -> Any:
        """Evaluate the metric with deprecation warning."""
        warnings.warn(
            "V3 metrics are deprecated and will be removed in a future version. "
            "Please migrate to V4 metrics for continued support and enhanced features. "
            "See the migration guide for more details: https://trustwiseai.github.io/tw-docs/docs/migration_guide",
            FutureWarning,
            stacklevel=3
        )
        return await self._metric.evaluate(*args, **kwargs)
    
    async def batch_evaluate(self, *args: Any, **kwargs: Any) -> Any:
        """Batch evaluate the metric with deprecation warning."""
        warnings.warn(
            "V3 metrics are deprecated and will be removed in a future version. "
            "Please migrate to V4 metrics for continued support and enhanced features. "
            "See the migration guide for more details: https://trustwiseai.github.io/tw-docs/docs/migration_guide",
            FutureWarning,
            stacklevel=3
        )
        return await self._metric.batch_evaluate(*args, **kwargs)

class MetricsV3Async:
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.adherence = AdherenceMetricAsync(client)
        self.faithfulness = FaithfulnessMetricAsync(client)
        self.answer_relevancy = AnswerRelevancyMetricAsync(client)
        self.context_relevancy = ContextRelevancyMetricAsync(client)
        self.summarization = SummarizationMetricAsync(client)
        self.pii = PIIMetricAsync(client)
        self.prompt_injection = PromptInjectionMetricAsync(client)
        self.clarity = ClarityMetricAsync(client)
        self.formality = FormalityMetricAsync(client)
        self.helpfulness = HelpfulnessMetricAsync(client)
        self.simplicity = SimplicityMetricAsync(client)
        self.tone = ToneMetricAsync(client)
        self.toxicity = ToxicityMetricAsync(client)
        self.sensitivity = SensitivityMetricAsync(client)
        self.refusal = RefusalMetricAsync(client)
        self.stability = StabilityMetricAsync(client)
        self.completion = CompletionMetricAsync(client)
        self.cost = CostMetricAsync(client)
        self.carbon = CarbonMetricAsync(client)

class MetricsV4Async:
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.answer_relevancy = AnswerRelevancyMetricAsyncV4(client)
        self.clarity = ClarityMetricAsyncV4(client)
        self.context_relevancy = ContextRelevancyMetricAsyncV4(client)
        self.faithfulness = FaithfulnessMetricAsyncV4(client)
        self.formality = FormalityMetricAsyncV4(client)
        self.helpfulness = HelpfulnessMetricAsyncV4(client)
        self.prompt_manipulation = PromptManipulationMetricAsyncV4(client)
        self.simplicity = SimplicityMetricAsyncV4(client)
        self.sensitivity = SensitivityMetricAsyncV4(client)
        self.tone = ToneMetricAsyncV4(client)
        self.toxicity = ToxicityMetricAsyncV4(client)
        self.pii = PIIMetricAsyncV4(client)
        self.refusal = RefusalMetricAsyncV4(client)
        self.completion = CompletionMetricAsyncV4(client)
        self.adherence = AdherenceMetricAsyncV4(client)
        self.stability = StabilityMetricAsyncV4(client)

class MetricsAsync:
    def __init__(self, client: TrustwiseAsyncClient) -> None:
        self.v3 = MetricsV3Async(client)
        self.v4 = MetricsV4Async(client)
        # Expose v3 metrics directly with deprecation warnings
        self.adherence = DeprecatedMetricWrapperAsync(self.v3.adherence)
        self.faithfulness = DeprecatedMetricWrapperAsync(self.v3.faithfulness)
        self.answer_relevancy = DeprecatedMetricWrapperAsync(self.v3.answer_relevancy)
        self.context_relevancy = DeprecatedMetricWrapperAsync(self.v3.context_relevancy)
        self.summarization = DeprecatedMetricWrapperAsync(self.v3.summarization)
        self.pii = DeprecatedMetricWrapperAsync(self.v3.pii)
        self.prompt_injection = DeprecatedMetricWrapperAsync(self.v3.prompt_injection)
        self.clarity = DeprecatedMetricWrapperAsync(self.v3.clarity)
        self.formality = DeprecatedMetricWrapperAsync(self.v3.formality)
        self.helpfulness = DeprecatedMetricWrapperAsync(self.v3.helpfulness)
        self.simplicity = DeprecatedMetricWrapperAsync(self.v3.simplicity)
        self.tone = DeprecatedMetricWrapperAsync(self.v3.tone)
        self.toxicity = DeprecatedMetricWrapperAsync(self.v3.toxicity)
        self.sensitivity = DeprecatedMetricWrapperAsync(self.v3.sensitivity)
        self.refusal = DeprecatedMetricWrapperAsync(self.v3.refusal)
        self.stability = DeprecatedMetricWrapperAsync(self.v3.stability)
        self.completion = DeprecatedMetricWrapperAsync(self.v3.completion)
        self.cost = DeprecatedMetricWrapperAsync(self.v3.cost)
        self.carbon = DeprecatedMetricWrapperAsync(self.v3.carbon)

    @property
    def version(self) -> str:
        return "v3"

class TrustwiseSDKAsync:
    """
    Async SDK entrypoint for Trustwise. Use this class to access async metrics.
    """
    def __init__(self, config: TrustwiseConfig) -> None:
        """
        Initialize the Trustwise SDK with path-based versioning support.

        Args:
            config: Trustwise configuration instance.
        """
        self.client = TrustwiseAsyncClient(config)
        self.metrics = MetricsAsync(self.client) 
import warnings
from typing import Any

from trustwise.sdk.metrics.v3 import (
    AdherenceMetric,
    AnswerRelevancyMetric,
    CarbonMetric,
    ClarityMetric,
    CompletionMetric,
    ContextRelevancyMetric,
    CostMetric,
    FaithfulnessMetric,
    FormalityMetric,
    HelpfulnessMetric,
    PIIMetric,
    PromptInjectionMetric,
    RefusalMetric,
    SensitivityMetric,
    SimplicityMetric,
    StabilityMetric,
    SummarizationMetric,
    ToneMetric,
    ToxicityMetric,
)
from trustwise.sdk.metrics.v4 import (
    AdherenceMetric as AdherenceMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    AnswerRelevancyMetric as AnswerRelevancyMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    ClarityMetric as ClarityMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    CompletionMetric as CompletionMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    ContextRelevancyMetric as ContextRelevancyMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    FaithfulnessMetric as FaithfulnessMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    FormalityMetric as FormalityMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    HelpfulnessMetric as HelpfulnessMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    PIIMetric as PIIMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    PromptManipulationMetric,
)
from trustwise.sdk.metrics.v4 import (
    RefusalMetric as RefusalMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    SensitivityMetric as SensitivityMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    SimplicityMetric as SimplicityMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    StabilityMetric as StabilityMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    ToneMetric as ToneMetricV4,
)
from trustwise.sdk.metrics.v4 import (
    ToxicityMetric as ToxicityMetricV4,
)


class DeprecatedMetricWrapper:
    """Wrapper class that adds deprecation warnings to v3 metrics."""
    
    def __init__(self, metric_instance: Any) -> None:
        self._metric = metric_instance
        
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the wrapped metric."""
        return getattr(self._metric, name)
    
    def evaluate(self, *args: Any, **kwargs: Any) -> Any:
        """Evaluate the metric with deprecation warning."""
        warnings.warn(
            "V3 metrics are deprecated and will be removed in a future version. "
            "Please migrate to V4 metrics for continued support and enhanced features. "
            "See the migration guide for more details: https://trustwiseai.github.io/tw-docs/docs/migration_guide",
            FutureWarning,
            stacklevel=3
        )
        return self._metric.evaluate(*args, **kwargs)
    
    def batch_evaluate(self, *args: Any, **kwargs: Any) -> Any:
        """Batch evaluate the metric with deprecation warning."""
        warnings.warn(
            "V3 metrics are deprecated and will be removed in a future version. "
            "Please migrate to V4 metrics for continued support and enhanced features. "
            "See the migration guide for more details: https://trustwiseai.github.io/tw-docs/docs/migration_guide",
            FutureWarning,
            stacklevel=3
        )
        return self._metric.batch_evaluate(*args, **kwargs)


class MetricsV3:
    def __init__(self, client: Any) -> None:
        self.adherence = AdherenceMetric(client)
        self.faithfulness = FaithfulnessMetric(client)
        self.answer_relevancy = AnswerRelevancyMetric(client)
        self.context_relevancy = ContextRelevancyMetric(client)
        self.summarization = SummarizationMetric(client)
        self.pii = PIIMetric(client)
        self.prompt_injection = PromptInjectionMetric(client)
        self.clarity = ClarityMetric(client)
        self.formality = FormalityMetric(client)
        self.helpfulness = HelpfulnessMetric(client)
        self.simplicity = SimplicityMetric(client)
        self.tone = ToneMetric(client)
        self.toxicity = ToxicityMetric(client)
        self.sensitivity = SensitivityMetric(client)
        self.refusal = RefusalMetric(client)
        self.stability = StabilityMetric(client)
        self.completion = CompletionMetric(client)
        self.cost = CostMetric(client)
        self.carbon = CarbonMetric(client)


class MetricsV4:
    def __init__(self, client: Any) -> None:
        self.prompt_manipulation = PromptManipulationMetric(client)
        self.answer_relevancy = AnswerRelevancyMetricV4(client)
        self.context_relevancy = ContextRelevancyMetricV4(client)
        self.faithfulness = FaithfulnessMetricV4(client)
        self.formality = FormalityMetricV4(client)
        self.clarity = ClarityMetricV4(client)
        self.helpfulness = HelpfulnessMetricV4(client)
        self.simplicity = SimplicityMetricV4(client)
        self.sensitivity = SensitivityMetricV4(client)
        self.tone = ToneMetricV4(client)
        self.toxicity = ToxicityMetricV4(client)
        self.pii = PIIMetricV4(client)
        self.refusal = RefusalMetricV4(client)
        self.completion = CompletionMetricV4(client)
        self.adherence = AdherenceMetricV4(client)
        self.stability = StabilityMetricV4(client)

class Metrics:
    def __init__(self, client: Any) -> None:
        self.v3 = MetricsV3(client)
        self.v4 = MetricsV4(client)
        # Expose v3 metrics directly with deprecation warnings
        self.adherence = DeprecatedMetricWrapper(self.v3.adherence)
        self.faithfulness = DeprecatedMetricWrapper(self.v3.faithfulness)
        self.answer_relevancy = DeprecatedMetricWrapper(self.v3.answer_relevancy)
        self.context_relevancy = DeprecatedMetricWrapper(self.v3.context_relevancy)
        self.summarization = DeprecatedMetricWrapper(self.v3.summarization)
        self.pii = DeprecatedMetricWrapper(self.v3.pii)
        self.prompt_injection = DeprecatedMetricWrapper(self.v3.prompt_injection)
        self.clarity = DeprecatedMetricWrapper(self.v3.clarity)
        self.formality = DeprecatedMetricWrapper(self.v3.formality)
        self.helpfulness = DeprecatedMetricWrapper(self.v3.helpfulness)
        self.simplicity = DeprecatedMetricWrapper(self.v3.simplicity)
        self.tone = DeprecatedMetricWrapper(self.v3.tone)
        self.toxicity = DeprecatedMetricWrapper(self.v3.toxicity)
        self.sensitivity = DeprecatedMetricWrapper(self.v3.sensitivity)
        self.refusal = DeprecatedMetricWrapper(self.v3.refusal)
        self.stability = DeprecatedMetricWrapper(self.v3.stability)
        self.completion = DeprecatedMetricWrapper(self.v3.completion)
        self.cost = DeprecatedMetricWrapper(self.v3.cost)
        self.carbon = DeprecatedMetricWrapper(self.v3.carbon)

    @property
    def version(self) -> str:
        return "v3"

__all__ = ["Metrics", "MetricsV3"] 
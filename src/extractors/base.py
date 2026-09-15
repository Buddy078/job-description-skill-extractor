import abc
from typing import Dict, Any, Optional
from ..models.schemas import ExtractionResult, JobPostingExtraction


class BaseExtractor(abc.ABC):
    """Abstract base class for all job description entity extractors."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abc.abstractmethod
    def extract(self, text: str) -> ExtractionResult:
        """Extract structured entities from raw job description text."""
        pass

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model_name: str = "gemini-3.8-flash") -> float:
        """Estimate cost in USD based on current standard token pricing.
        Gemini 3.8 Flash pricing: ~$0.15 / 1M prompt tokens, ~$0.60 / 1M completion tokens.
        """
        if "flash" in model_name.lower():
            cost_input = (prompt_tokens / 1_000_000.0) * 0.15
            cost_output = (completion_tokens / 1_000_000.0) * 0.60
            return round(cost_input + cost_output, 6)
        elif "pro" in model_name.lower():
            cost_input = (prompt_tokens / 1_000_000.0) * 1.25
            cost_output = (completion_tokens / 1_000_000.0) * 5.00
            return round(cost_input + cost_output, 6)
        return 0.0

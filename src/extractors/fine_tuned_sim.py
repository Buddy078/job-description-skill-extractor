import time
from typing import Optional, Dict, Any, List
from ..models.schemas import (
    JobPostingExtraction,
    ExtractionResult,
    SkillItem,
    SkillCategory,
    ToolItem,
    QualificationItem,
    DegreeLevel,
    CertificationItem,
    ExperienceRequirement,
    SeniorityLevel,
)
from .base import BaseExtractor
from .rule_based import RuleBasedExtractor


class FineTunedModelSimulator(BaseExtractor):
    """Represents a fine-tuned domain-specific smaller model (e.g. Llama-3-8B-Instruct or
    specialized BIO sequence tagger fine-tuned on annotated job descriptions).
    Offers ultra-low inference latency, predictable formatting, and zero external API fees,
    with potential trade-offs in generalizing to brand new niche tools.
    """

    def __init__(self, model_checkpoint: str = "checkpoints/jd-skill-ner-v1"):
        super().__init__(
            name="fine_tuned_model",
            description=f"Specialized fine-tuned sequence-to-sequence model ({model_checkpoint})",
        )
        self.model_checkpoint = model_checkpoint
        self.rule_based = RuleBasedExtractor()

    def extract(self, text: str) -> ExtractionResult:
        start_time = time.perf_counter()
        
        # Simulate neural model processing
        base_res = self.rule_based.extract(text)
        extraction = base_res.extraction

        # Fine-tuned models have high accuracy on in-domain skills, with slight simulated latency (e.g. 50-80ms)
        time.sleep(0.04)  # 40ms simulated forward pass

        latency = (time.perf_counter() - start_time) * 1000.0

        # Estimate tokens
        p_tokens = len(text) // 4
        c_tokens = 320

        return ExtractionResult(
            extraction_method=self.name,
            success=True,
            extraction=extraction,
            latency_ms=round(latency, 2),
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            total_tokens=p_tokens + c_tokens,
            estimated_cost_usd=0.0,  # Self-hosted / local weights
            raw_response=f"[Fine-Tuned Checkpoint: {self.model_checkpoint}] Structured JSON Output generated via greedy search.",
            is_schema_compliant=True,
            validation_errors=[],
            notes=f"Self-hosted weights ({self.model_checkpoint}). Predictable low latency, zero external API costs.",
        )

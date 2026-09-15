import pytest
from src.extractors.prompt_based import PromptBasedExtractor
from src.extractors.structured_output import StructuredOutputExtractor
from src.extractors.fine_tuned_sim import FineTunedModelSimulator


def test_prompt_based_extractor():
    extractor = PromptBasedExtractor()
    text = "Hiring a Software Engineer with Python and Docker skills. 3+ years experience."
    res = extractor.extract(text)
    assert res.success is True
    assert res.extraction is not None
    # Simulated prompt-based output uses code fences so schema_compliant should be False
    assert res.is_schema_compliant is False
    assert len(res.validation_errors) > 0


def test_structured_output_extractor():
    extractor = StructuredOutputExtractor()
    text = "Hiring a Software Engineer with Python and Docker skills. 3+ years experience."
    res = extractor.extract(text)
    assert res.success is True
    assert res.extraction is not None
    assert res.is_schema_compliant is True
    assert len(res.validation_errors) == 0


def test_fine_tuned_simulator():
    sim = FineTunedModelSimulator()
    text = "Seeking Senior Data Engineer with Python, Spark, and AWS."
    res = sim.extract(text)
    assert res.success is True
    assert res.extraction is not None
    assert res.is_schema_compliant is True
    assert res.estimated_cost_usd == 0.0

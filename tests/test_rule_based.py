import pytest
from src.extractors.rule_based import RuleBasedExtractor
from src.models.schemas import SeniorityLevel, DegreeLevel


@pytest.fixture
def extractor():
    return RuleBasedExtractor()


def test_extract_technical_and_soft_skills(extractor):
    text = """
    We need a Python and C++ programmer.
    You must be an expert in distributed systems, microservices, and concurrency.
    Strong problem-solving and communication skills are required.
    """
    res = extractor.extract(text)
    assert res.success is True
    tech_names = {s.name for s in res.extraction.technical_skills}
    soft_names = {s.name for s in res.extraction.soft_skills}

    assert "Python" in tech_names
    assert "C++" in tech_names
    assert "Distributed Systems" in tech_names
    assert "Microservices" in tech_names
    assert "Concurrency / Multithreading" in tech_names
    assert "Problem Solving" in soft_names
    assert "Communication Skills" in soft_names


def test_extract_tools_and_qualifications(extractor):
    text = """
    Position: Senior DevOps Engineer
    Required: Docker, Kubernetes, Terraform, and AWS.
    Optional / Plus: Redis and MongoDB.
    Education: Must have Bachelor's degree in Software Engineering.
    Certifications: Certified Kubernetes Administrator (CKA).
    """
    res = extractor.extract(text)
    assert res.success is True
    tool_map = {t.name: t.is_required for t in res.extraction.tools_and_technologies}
    assert "Docker" in tool_map
    assert "Kubernetes" in tool_map
    assert "AWS" in tool_map

    quals = res.extraction.qualifications
    assert len(quals) > 0
    assert quals[0].degree == DegreeLevel.BACHELORS

    certs = [c.name for c in res.extraction.certifications]
    assert "Certified Kubernetes Administrator (CKA)" in certs


def test_extract_experience_years_range(extractor):
    text = """
    Requires 5 to 8 years of experience in cloud infrastructure.
    """
    res = extractor.extract(text)
    assert len(res.extraction.experience_requirements) > 0
    exp = res.extraction.experience_requirements[0]
    assert exp.min_years == 5.0
    assert exp.max_years == 8.0


def test_empty_or_unrelated_text(extractor):
    text = "A sunny day in the park with birds singing."
    res = extractor.extract(text)
    assert res.success is True
    assert len(res.extraction.technical_skills) == 0
    assert len(res.extraction.soft_skills) == 0

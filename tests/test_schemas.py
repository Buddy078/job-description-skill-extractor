import pytest
from src.models.schemas import (
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


def test_job_posting_extraction_defaults():
    extraction = JobPostingExtraction()
    assert extraction.job_title is None
    assert extraction.seniority_level == SeniorityLevel.NOT_SPECIFIED
    assert len(extraction.technical_skills) == 0
    assert len(extraction.soft_skills) == 0
    assert len(extraction.tools_and_technologies) == 0


def test_schema_serialization_and_validation():
    data = {
        "job_title": "Lead Software Architect",
        "seniority_level": "Lead / Staff",
        "technical_skills": [
            {"name": "Python", "category": "technical", "proficiency_level": "Expert"}
        ],
        "soft_skills": [
            {"name": "Mentorship", "category": "soft"}
        ],
        "tools_and_technologies": [
            {"name": "Kubernetes", "purpose": "Orchestration", "is_required": True}
        ],
        "qualifications": [
            {"degree": "Master's (MS / MA)", "field_of_study": "Computer Science"}
        ],
        "certifications": [
            {"name": "CKA", "issuing_body": "CNCF", "is_required": False}
        ],
        "experience_requirements": [
            {"min_years": 8.0, "seniority_level": "Lead / Staff", "domain_area": "Cloud Architecture"}
        ],
        "summary": "Experienced Lead Architect sought.",
    }

    model = JobPostingExtraction.model_validate(data)
    assert model.job_title == "Lead Software Architect"
    assert model.seniority_level == SeniorityLevel.LEAD
    assert model.technical_skills[0].name == "Python"
    assert model.technical_skills[0].category == SkillCategory.TECHNICAL
    assert model.qualifications[0].degree == DegreeLevel.MASTERS

    json_str = model.model_dump_json()
    reloaded = JobPostingExtraction.model_validate_json(json_str)
    assert reloaded.job_title == model.job_title


def test_extraction_result_envelope():
    res = ExtractionResult(
        extraction_method="structured_output",
        success=True,
        extraction=JobPostingExtraction(job_title="DevOps Engineer"),
        latency_ms=12.4,
        prompt_tokens=400,
        completion_tokens=150,
        total_tokens=550,
        estimated_cost_usd=0.00015,
        is_schema_compliant=True,
    )
    assert res.success is True
    assert res.is_schema_compliant is True
    assert res.extraction.job_title == "DevOps Engineer"

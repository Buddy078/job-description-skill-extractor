import pytest
from src.evaluation.metrics import (
    normalize_entity_name,
    calculate_set_metrics,
    evaluate_extraction,
)
from src.models.schemas import (
    JobPostingExtraction,
    SkillItem,
    SkillCategory,
    ToolItem,
    QualificationItem,
    DegreeLevel,
    ExperienceRequirement,
)


def test_normalize_entity_name():
    assert normalize_entity_name("Go (Golang)") == "go"
    assert normalize_entity_name("PostgreSQL") == "postgresql"
    assert normalize_entity_name("Amazon Web Services") == "aws"
    assert normalize_entity_name("React.js") == "react"


def test_calculate_set_metrics():
    pred = {"Python", "Docker", "AWS", "K8s"}
    gt = {"Python", "Docker", "AWS", "Kubernetes"}
    
    metrics = calculate_set_metrics(pred, gt)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0


def test_evaluate_extraction():
    gt = JobPostingExtraction(
        technical_skills=[SkillItem(name="Python", category=SkillCategory.TECHNICAL)],
        tools_and_technologies=[ToolItem(name="Docker", purpose="Container")],
        qualifications=[QualificationItem(degree=DegreeLevel.BACHELORS)],
        experience_requirements=[ExperienceRequirement(min_years=5.0)],
    )

    pred = JobPostingExtraction(
        technical_skills=[SkillItem(name="Python", category=SkillCategory.TECHNICAL)],
        tools_and_technologies=[ToolItem(name="Docker", purpose="Container")],
        qualifications=[QualificationItem(degree=DegreeLevel.BACHELORS)],
        experience_requirements=[ExperienceRequirement(min_years=5.0)],
    )

    eval_result = evaluate_extraction(pred, gt, is_schema_compliant=True, latency_ms=10.0)
    assert eval_result["overall_f1"] == 1.0
    assert eval_result["schema_compliant"] is True
    assert eval_result["qualifications_match"] is True
    assert eval_result["experience_match"] is True

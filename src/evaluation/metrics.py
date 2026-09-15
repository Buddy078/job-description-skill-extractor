import re
from typing import List, Set, Dict, Any, Tuple, Optional
from ..models.schemas import JobPostingExtraction, ExtractionResult


def normalize_entity_name(name: str) -> str:
    """Normalize entity name for fair semantic matching (e.g. 'Go (Golang)' -> 'go')."""
    if not name:
        return ""
    # Remove parenthetical details
    cleaned = re.sub(r"\([^)]*\)", "", name)
    # Remove punctuation & lowercase
    cleaned = re.sub(r"[^a-zA-Z0-9+#]", " ", cleaned).lower().strip()
    # Canonical mappings
    synonyms = {
        "golang": "go",
        "postgres": "postgresql",
        "k8s": "kubernetes",
        "amazon web services": "aws",
        "google cloud": "gcp",
        "google cloud platform": "gcp",
        "microsoft azure": "azure",
        "js": "javascript",
        "ts": "typescript",
        "reactjs": "react",
        "react js": "react",
        "react.js": "react",
        "vuejs": "vue",
        "vue js": "vue",
        "nodejs": "node",
        "node js": "node",
        "node.js": "node",
    }
    return synonyms.get(cleaned, cleaned)


def calculate_set_metrics(predicted: Set[str], ground_truth: Set[str]) -> Dict[str, float]:
    """Calculates Precision, Recall, and F1 score between two sets of normalized strings."""
    if not predicted and not ground_truth:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "tp": 0, "fp": 0, "fn": 0}
    if not predicted:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "tp": 0, "fp": 0, "fn": len(ground_truth)}
    if not ground_truth:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "tp": 0, "fp": len(predicted), "fn": 0}

    # Match based on normalized equality or substantial substring overlap
    tp_matches = set()
    for p in predicted:
        norm_p = normalize_entity_name(p)
        for g in ground_truth:
            norm_g = normalize_entity_name(g)
            if norm_p == norm_g or (len(norm_p) > 3 and norm_p in norm_g) or (len(norm_g) > 3 and norm_g in norm_p):
                tp_matches.add(p)
                break

    tp = len(tp_matches)
    fp = len(predicted) - tp
    fn = len(ground_truth) - tp

    precision = tp / len(predicted) if predicted else 0.0
    recall = tp / len(ground_truth) if ground_truth else 0.0
    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def evaluate_extraction(
    predicted: Optional[JobPostingExtraction],
    ground_truth: JobPostingExtraction,
    is_schema_compliant: bool = True,
    latency_ms: float = 0.0,
    cost_usd: float = 0.0,
) -> Dict[str, Any]:
    """Comprehensive evaluation of a single extraction against ground truth."""
    if not predicted:
        return {
            "overall_f1": 0.0,
            "overall_precision": 0.0,
            "overall_recall": 0.0,
            "technical_skills": calculate_set_metrics(set(), {s.name for s in ground_truth.technical_skills}),
            "soft_skills": calculate_set_metrics(set(), {s.name for s in ground_truth.soft_skills}),
            "tools": calculate_set_metrics(set(), {t.name for t in ground_truth.tools_and_technologies}),
            "qualifications_match": False,
            "experience_match": False,
            "schema_compliant": False,
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
        }

    # Technical skills
    p_tech = {s.name for s in predicted.technical_skills}
    g_tech = {s.name for s in ground_truth.technical_skills}
    tech_metrics = calculate_set_metrics(p_tech, g_tech)

    # Soft skills
    p_soft = {s.name for s in predicted.soft_skills}
    g_soft = {s.name for s in ground_truth.soft_skills}
    soft_metrics = calculate_set_metrics(p_soft, g_soft)

    # Tools
    p_tools = {t.name for t in predicted.tools_and_technologies}
    g_tools = {t.name for t in ground_truth.tools_and_technologies}
    tool_metrics = calculate_set_metrics(p_tools, g_tools)

    # Degrees / Qualifications
    p_degrees = {q.degree for q in predicted.qualifications}
    g_degrees = {q.degree for q in ground_truth.qualifications}
    degree_overlap = len(p_degrees.intersection(g_degrees)) > 0 or (not p_degrees and not g_degrees)

    # Experience Years match
    p_exp_min = [e.min_years for e in predicted.experience_requirements if e.min_years is not None]
    g_exp_min = [e.min_years for e in ground_truth.experience_requirements if e.min_years is not None]
    exp_match = False
    if p_exp_min and g_exp_min:
        exp_match = abs(p_exp_min[0] - g_exp_min[0]) <= 1.0
    elif not p_exp_min and not g_exp_min:
        exp_match = True

    # Weighted macro average across entities
    avg_precision = (tech_metrics["precision"] + soft_metrics["precision"] + tool_metrics["precision"]) / 3.0
    avg_recall = (tech_metrics["recall"] + soft_metrics["recall"] + tool_metrics["recall"]) / 3.0
    avg_f1 = (tech_metrics["f1"] + soft_metrics["f1"] + tool_metrics["f1"]) / 3.0

    return {
        "overall_f1": round(avg_f1, 4),
        "overall_precision": round(avg_precision, 4),
        "overall_recall": round(avg_recall, 4),
        "technical_skills": tech_metrics,
        "soft_skills": soft_metrics,
        "tools": tool_metrics,
        "qualifications_match": degree_overlap,
        "experience_match": exp_match,
        "schema_compliant": is_schema_compliant,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
    }

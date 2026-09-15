import time
from typing import List, Dict, Any, Optional
import pandas as pd

from ..models.schemas import ExtractionResult, JobPostingExtraction
from ..extractors.base import BaseExtractor
from ..extractors.rule_based import RuleBasedExtractor
from ..extractors.prompt_based import PromptBasedExtractor
from ..extractors.structured_output import StructuredOutputExtractor
from ..extractors.fine_tuned_sim import FineTunedModelSimulator
from ..dataset.benchmark_dataset import BENCHMARK_DATASET, get_all_benchmark_jobs
from .metrics import evaluate_extraction


class PipelineComparator:
    """Orchestrates head-to-head comparisons across extraction approaches:
    - Prompt-Based (Few-shot natural language JSON request)
    - Structured-Output (Gemini response_format schema enforcement)
    - Rule-Based / Pattern NER (Deterministic local baseline)
    - Fine-Tuned Model (Specialized sequence tagger simulation)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.extractors: Dict[str, BaseExtractor] = {
            "Prompt-Based": PromptBasedExtractor(api_key=api_key),
            "Structured-Output": StructuredOutputExtractor(api_key=api_key),
            "Rule-Based NER": RuleBasedExtractor(),
            "Fine-Tuned Model": FineTunedModelSimulator(),
        }

    def compare_single_text(self, text: str, ground_truth: Optional[JobPostingExtraction] = None) -> Dict[str, Any]:
        """Runs all extractors on a single job description text and returns comparative results."""
        results = {}
        for name, extractor in self.extractors.items():
            res: ExtractionResult = extractor.extract(text)
            eval_data = None
            if ground_truth:
                eval_data = evaluate_extraction(
                    predicted=res.extraction,
                    ground_truth=ground_truth,
                    is_schema_compliant=res.is_schema_compliant,
                    latency_ms=res.latency_ms,
                    cost_usd=res.estimated_cost_usd,
                )
            results[name] = {
                "result": res,
                "evaluation": eval_data,
            }
        return results

    def run_benchmark_suite(self, max_samples: Optional[int] = None) -> pd.DataFrame:
        """Runs full benchmark suite against gold-standard annotated dataset."""
        dataset = BENCHMARK_DATASET[:max_samples] if max_samples else BENCHMARK_DATASET
        records = []

        for name, extractor in self.extractors.items():
            total_latency = 0.0
            total_tokens = 0
            total_cost = 0.0
            compliant_count = 0
            f1_scores = []
            precision_scores = []
            recall_scores = []
            tech_f1s = []
            soft_f1s = []
            tool_f1s = []

            for item in dataset:
                raw_text = item["raw_text"]
                gt = item["ground_truth"]

                res: ExtractionResult = extractor.extract(raw_text)
                eval_metrics = evaluate_extraction(
                    predicted=res.extraction,
                    ground_truth=gt,
                    is_schema_compliant=res.is_schema_compliant,
                    latency_ms=res.latency_ms,
                    cost_usd=res.estimated_cost_usd,
                )

                total_latency += res.latency_ms
                total_tokens += res.total_tokens
                total_cost += res.estimated_cost_usd
                if res.is_schema_compliant:
                    compliant_count += 1

                f1_scores.append(eval_metrics["overall_f1"])
                precision_scores.append(eval_metrics["overall_precision"])
                recall_scores.append(eval_metrics["overall_recall"])
                tech_f1s.append(eval_metrics["technical_skills"]["f1"])
                soft_f1s.append(eval_metrics["soft_skills"]["f1"])
                tool_f1s.append(eval_metrics["tools"]["f1"])

            n = len(dataset)
            records.append({
                "Method": name,
                "Avg Latency (ms)": round(total_latency / n, 1),
                "Schema Compliance Rate (%)": round((compliant_count / n) * 100.0, 1),
                "Overall F1 Score": round(sum(f1_scores) / n, 3),
                "Overall Precision": round(sum(precision_scores) / n, 3),
                "Overall Recall": round(sum(recall_scores) / n, 3),
                "Tech Skills F1": round(sum(tech_f1s) / n, 3),
                "Soft Skills F1": round(sum(soft_f1s) / n, 3),
                "Tools F1": round(sum(tool_f1s) / n, 3),
                "Avg Tokens / JD": int(total_tokens / n),
                "Est. Cost / 1k JDs ($)": round((total_cost / n) * 1000.0, 3),
            })

        return pd.DataFrame(records)

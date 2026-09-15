import argparse
import sys
import json
from pathlib import Path
import pandas as pd

from .extractors.rule_based import RuleBasedExtractor
from .extractors.prompt_based import PromptBasedExtractor
from .extractors.structured_output import StructuredOutputExtractor
from .extractors.fine_tuned_sim import FineTunedModelSimulator
from .evaluation.comparator import PipelineComparator
from .dataset.fine_tuning_generator import FineTuningDataGenerator
from .dataset.benchmark_dataset import BENCHMARK_DATASET


def cmd_extract(args):
    text = ""
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        print("Error: Specify either --file or --text", file=sys.stderr)
        sys.exit(1)

    extractors = {
        "rule": RuleBasedExtractor(),
        "prompt": PromptBasedExtractor(),
        "structured": StructuredOutputExtractor(),
        "finetuned": FineTunedModelSimulator(),
    }

    if args.method == "all":
        comparator = PipelineComparator()
        results = comparator.compare_single_text(text)
        for name, data in results.items():
            res = data["result"]
            print(f"\n================ {name} ================")
            print(f"Success: {res.success} | Schema Compliant: {res.is_schema_compliant} | Latency: {res.latency_ms}ms | Cost: ${res.estimated_cost_usd:.5f}")
            if res.extraction:
                print(f"Title: {res.extraction.job_title} ({res.extraction.seniority_level.value})")
                print(f"Tech Skills ({len(res.extraction.technical_skills)}): {[s.name for s in res.extraction.technical_skills]}")
                print(f"Soft Skills ({len(res.extraction.soft_skills)}): {[s.name for s in res.extraction.soft_skills]}")
                print(f"Tools ({len(res.extraction.tools_and_technologies)}): {[t.name for t in res.extraction.tools_and_technologies]}")
                print(f"Qualifications: {[q.degree.value for q in res.extraction.qualifications]}")
                print(f"Certifications: {[c.name for c in res.extraction.certifications]}")
                print(f"Experience: {[(e.min_years, e.domain_area) for e in res.extraction.experience_requirements]}")
            if res.validation_errors:
                print(f"Validation warnings/errors: {res.validation_errors}")
    else:
        extractor = extractors.get(args.method)
        if not extractor:
            print(f"Unknown method: {args.method}. Choose from rule, prompt, structured, finetuned, all.", file=sys.stderr)
            sys.exit(1)
        res = extractor.extract(text)
        if args.json:
            print(json.dumps(res.model_dump(), indent=2))
        else:
            print(f"Method: {res.extraction_method}")
            print(f"Success: {res.success} | Schema Compliant: {res.is_schema_compliant}")
            print(f"Latency: {res.latency_ms} ms | Total Tokens: {res.total_tokens}")
            if res.extraction:
                print(f"\nJob Title: {res.extraction.job_title}")
                print(f"Seniority: {res.extraction.seniority_level.value}")
                print(f"Technical Skills: {[s.name for s in res.extraction.technical_skills]}")
                print(f"Soft Skills: {[s.name for s in res.extraction.soft_skills]}")
                print(f"Tools & Tech: {[t.name for t in res.extraction.tools_and_technologies]}")
                print(f"Qualifications: {[q.degree.value for q in res.extraction.qualifications]}")
                print(f"Certifications: {[c.name for c in res.extraction.certifications]}")
                print(f"Experience Requirements: {[(e.min_years, e.domain_area) for e in res.extraction.experience_requirements]}")


def cmd_benchmark(args):
    print("Running evaluation benchmark suite against gold-standard dataset...")
    comparator = PipelineComparator()
    df = comparator.run_benchmark_suite()
    print("\n" + df.to_string(index=False))
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.suffix == ".json":
            df.to_json(out_path, orient="records", indent=2)
        elif out_path.suffix == ".csv":
            df.to_csv(out_path, index=False)
        print(f"\nBenchmark results saved to: {out_path}")


def cmd_export_dataset(args):
    generator = FineTuningDataGenerator()
    out_file = generator.export_to_file(args.output, format_type=args.format)
    print(f"Exported dataset in '{args.format}' format to: {out_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Job Description Skill Extractor: High-fidelity information extraction & benchmark CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # extract command
    p_extract = subparsers.add_parser("extract", help="Extract entities from job description text or file")
    p_extract.add_argument("--file", "-f", help="Path to job description text file")
    p_extract.add_argument("--text", "-t", help="Raw job description string")
    p_extract.add_argument("--method", "-m", default="structured", choices=["rule", "prompt", "structured", "finetuned", "all"], help="Extraction approach")
    p_extract.add_argument("--json", action="store_true", help="Output full result as JSON")
    p_extract.set_defaults(func=cmd_extract)

    # benchmark command
    p_bench = subparsers.add_parser("benchmark", help="Run full evaluation benchmark suite")
    p_bench.add_argument("--output", "-o", help="Optional path to save results (.json or .csv)")
    p_bench.set_defaults(func=cmd_benchmark)

    # export-dataset command
    p_export = subparsers.add_parser("export-dataset", help="Export fine-tuning training dataset")
    p_export.add_argument("--format", default="chat", choices=["chat", "instruction", "bio"], help="Target format")
    p_export.add_argument("--output", "-o", default="data/finetune_chat.jsonl", help="Output file path")
    p_export.set_defaults(func=cmd_export_dataset)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

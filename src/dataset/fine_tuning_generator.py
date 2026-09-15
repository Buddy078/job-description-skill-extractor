import json
import re
from pathlib import Path
from typing import List, Dict, Any
from .benchmark_dataset import BENCHMARK_DATASET

SYSTEM_PROMPT = """You are an expert recruitment and HR information-extraction assistant.
Analyze the input job description and extract structured technical skills, soft skills, tools, qualifications, certifications, and experience requirements as valid JSON."""


class FineTuningDataGenerator:
    """Generates fine-tuning datasets from annotated job descriptions in multiple target formats:
    1. Chat JSONL (Gemini 3.8 / OpenAI format with system, user, assistant messages)
    2. Instruction JSONL (Alpaca / HuggingFace format)
    3. BIO Sequence Tagging (token-level NER dataset)
    """

    def __init__(self, dataset: List[Dict[str, Any]] = None):
        self.dataset = dataset or BENCHMARK_DATASET

    def generate_chat_jsonl(self) -> List[Dict[str, Any]]:
        """Generates standard chat format for supervised fine-tuning (SFT)."""
        records = []
        for item in self.dataset:
            ground_truth_dict = item["ground_truth"].model_dump()
            assistant_content = json.dumps(ground_truth_dict, indent=2)
            record = {
                "id": item["id"],
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Extract structured information from this job description:\n\n{item['raw_text']}"},
                    {"role": "assistant", "content": assistant_content},
                ],
            }
            records.append(record)
        return records

    def generate_instruction_jsonl(self) -> List[Dict[str, Any]]:
        """Generates Alpaca-style instruction/input/output pairs."""
        records = []
        for item in self.dataset:
            ground_truth_dict = item["ground_truth"].model_dump()
            records.append({
                "instruction": "Extract all technical skills, soft skills, tools, qualifications, certifications, and experience from the job posting.",
                "input": item["raw_text"],
                "output": json.dumps(ground_truth_dict, indent=2),
            })
        return records

    def generate_bio_tagged_tokens(self) -> List[Dict[str, Any]]:
        """Generates tokenized BIO tags (Begin / Inside / Outside) for sequence labeling NER."""
        tagged_documents = []

        for item in self.dataset:
            text = item["raw_text"]
            gt = item["ground_truth"]

            # Tokenize by whitespace and punctuation
            tokens = re.findall(r"\w+|[^\w\s]", text)
            tags = ["O"] * len(tokens)

            # Mark target entities
            entity_targets = []
            for s in gt.technical_skills:
                entity_targets.append((s.name, "TECH"))
            for s in gt.soft_skills:
                entity_targets.append((s.name, "SOFT"))
            for t in gt.tools_and_technologies:
                entity_targets.append((t.name, "TOOL"))

            # Simple span matching over tokens
            token_str_lower = [tok.lower() for tok in tokens]
            for entity_name, tag_type in entity_targets:
                ent_tokens = [tok.lower() for tok in re.findall(r"\w+|[^\w\s]", entity_name)]
                ent_len = len(ent_tokens)
                if ent_len == 0:
                    continue
                for i in range(len(tokens) - ent_len + 1):
                    if token_str_lower[i : i + ent_len] == ent_tokens:
                        tags[i] = f"B-{tag_type}"
                        for j in range(1, ent_len):
                            tags[i + j] = f"I-{tag_type}"

            tagged_documents.append({
                "id": item["id"],
                "tokens": tokens,
                "bio_tags": tags,
                "entity_count": len(entity_targets),
            })

        return tagged_documents

    def export_to_file(self, output_path: str, format_type: str = "chat") -> str:
        """Export dataset to disk in the chosen format."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if format_type == "chat":
            data = self.generate_chat_jsonl()
            with open(out, "w", encoding="utf-8") as f:
                for row in data:
                    f.write(json.dumps(row) + "\n")
        elif format_type == "instruction":
            data = self.generate_instruction_jsonl()
            with open(out, "w", encoding="utf-8") as f:
                for row in data:
                    f.write(json.dumps(row) + "\n")
        elif format_type == "bio":
            data = self.generate_bio_tagged_tokens()
            with open(out, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unknown format: {format_type}")

        return str(out)

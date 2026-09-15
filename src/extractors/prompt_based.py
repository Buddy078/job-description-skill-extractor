import os
import json
import re
import time
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv

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

load_dotenv()

PROMPT_TEMPLATE = """You are an expert HR and technical recruiter information-extraction system.
Extract all relevant career information from the job description below.

You MUST respond ONLY with a JSON object containing:
- "job_title": string
- "seniority_level": string (e.g. "Entry-level / Junior", "Mid-level", "Senior", "Lead / Staff", "Principal / Director", "Not Specified")
- "technical_skills": list of objects [{"name": string, "category": "technical", "proficiency_level": string or null, "context_snippet": string or null}]
- "soft_skills": list of objects [{"name": string, "category": "soft", "proficiency_level": string or null, "context_snippet": string or null}]
- "tools_and_technologies": list of objects [{"name": string, "purpose": string or null, "is_required": boolean}]
- "qualifications": list of objects [{"degree": string, "field_of_study": string or null, "is_required": boolean, "raw_text": string or null}]
- "certifications": list of objects [{"name": string, "issuing_body": string or null, "is_required": boolean}]
- "experience_requirements": list of objects [{"min_years": float or null, "max_years": float or null, "seniority_level": string, "domain_area": string or null, "raw_text": string or null}]
- "summary": string (1-2 sentence summary)

Job Description:
<<<JD_TEXT>>>
"""


class PromptBasedExtractor(BaseExtractor):
    """Prompt-based extractor using natural language instructions.
    Does NOT use model-level schema constraints or response_format JSON schema.
    Prone to markdown fences, unexpected preamble/postamble, key hallucinations, and type coercions.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="prompt_based",
            description="Unconstrained natural language few-shot prompt (raw JSON request without schema enforcement)",
        )
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def _call_gemini_api(self, text: str) -> Tuple[str, int, int]:
        from google import genai
        client = genai.Client(api_key=self.api_key)
        prompt = PROMPT_TEMPLATE.replace('<<<JD_TEXT>>>', text)
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
        )
        raw_text = interaction.output_text or ""
        p_tokens = getattr(getattr(interaction, "usage", None), "prompt_tokens", len(prompt) // 4)
        c_tokens = getattr(getattr(interaction, "usage", None), "completion_tokens", len(raw_text) // 4)
        return raw_text, p_tokens, c_tokens

    def _simulate_prompt_response(self, text: str) -> Tuple[str, int, int]:
        # Offline realistic simulation of prompt-based output (with markdown fences & occasional preamble)
        from .rule_based import RuleBasedExtractor
        rb = RuleBasedExtractor()
        res = rb.extract(text)
        base_dict = res.extraction.model_dump()
        
        # In prompt-based extraction, LLMs commonly wrap in markdown fences:
        json_str = json.dumps(base_dict, indent=2)
        simulated_raw = f"```json\n{json_str}\n```"
        p_tokens = len(PROMPT_TEMPLATE.replace('<<<JD_TEXT>>>', text)) // 4
        c_tokens = len(simulated_raw) // 4
        return simulated_raw, p_tokens, c_tokens

    def _clean_and_parse_json(self, raw: str) -> Tuple[Optional[dict], bool, List[str]]:
        validation_errors = []
        is_schema_compliant = True

        # Check if model wrapped in markdown fences
        clean_text = raw.strip()
        if clean_text.startswith("```"):
            is_schema_compliant = False
            validation_errors.append("Output wrapped in markdown code fence (```json ... ```)")
            clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r"\\s*```$", "", clean_text)

        # Check for conversational preamble
        first_brace = clean_text.find("{")
        last_brace = clean_text.rfind("}")
        if first_brace != -1 and last_brace != -1:
            if first_brace > 0 or last_brace < len(clean_text) - 1:
                is_schema_compliant = False
                validation_errors.append("Conversational preamble or postamble detected before/after JSON")
                clean_text = clean_text[first_brace : last_brace + 1]
        
        try:
            parsed = json.loads(clean_text)
            return parsed, is_schema_compliant, validation_errors
        except json.JSONDecodeError as e:
            validation_errors.append(f"JSONDecodeError: {str(e)}")
            # Try basic recovery for trailing commas
            fixed_text = re.sub(r",\s*([\]}])", r"", clean_text)
            try:
                parsed = json.loads(fixed_text)
                validation_errors.append("Recovered from JSON trailing comma syntax error")
                return parsed, False, validation_errors
            except Exception:
                return None, False, validation_errors

    def extract(self, text: str) -> ExtractionResult:
        start_time = time.perf_counter()
        raw_output = ""
        prompt_tokens = 0
        completion_tokens = 0

        use_live_api = bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("mock"))

        try:
            if use_live_api:
                raw_output, prompt_tokens, completion_tokens = self._call_gemini_api(text)
            else:
                raw_output, prompt_tokens, completion_tokens = self._simulate_prompt_response(text)

            parsed_data, is_compliant, val_errors = self._clean_and_parse_json(raw_output)

            if parsed_data is None:
                latency = (time.perf_counter() - start_time) * 1000.0
                return ExtractionResult(
                    extraction_method=self.name,
                    success=False,
                    extraction=None,
                    latency_ms=round(latency, 2),
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    estimated_cost_usd=self.estimate_cost(prompt_tokens, completion_tokens),
                    raw_response=raw_output,
                    is_schema_compliant=False,
                    validation_errors=val_errors,
                    notes="Failed to parse JSON response from prompt-based generation.",
                )

            # Validate against Pydantic schema
            try:
                # Key normalization if prompt generated variants
                if "tech_skills" in parsed_data and "technical_skills" not in parsed_data:
                    parsed_data["technical_skills"] = parsed_data.pop("tech_skills")
                    val_errors.append("Remapped non-standard key 'tech_skills' -> 'technical_skills'")
                    is_compliant = False

                extraction_model = JobPostingExtraction.model_validate(parsed_data)
            except Exception as pe:
                val_errors.append(f"Pydantic Validation Error: {str(pe)}")
                is_compliant = False
                # Attempt best-effort loose construction
                extraction_model = None

            latency = (time.perf_counter() - start_time) * 1000.0
            return ExtractionResult(
                extraction_method=self.name,
                success=extraction_model is not None,
                extraction=extraction_model,
                latency_ms=round(latency, 2),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost_usd=self.estimate_cost(prompt_tokens, completion_tokens),
                raw_response=raw_output,
                is_schema_compliant=is_compliant,
                validation_errors=val_errors,
                notes="Standard prompt-based extraction. Subject to formatting drift and manual JSON cleaning.",
            )

        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000.0
            return ExtractionResult(
                extraction_method=self.name,
                success=False,
                extraction=None,
                latency_ms=round(latency, 2),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost_usd=0.0,
                raw_response=str(raw_output),
                is_schema_compliant=False,
                validation_errors=[str(e)],
                notes=f"Exception during extraction: {str(e)}",
            )

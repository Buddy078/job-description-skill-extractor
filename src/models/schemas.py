from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SkillCategory(str, Enum):
    TECHNICAL = "technical"
    SOFT = "soft"
    TOOL = "tool"
    DOMAIN = "domain"


class SeniorityLevel(str, Enum):
    ENTRY = "Entry-level / Junior"
    MID = "Mid-level"
    SENIOR = "Senior"
    LEAD = "Lead / Staff"
    PRINCIPAL = "Principal / Director"
    NOT_SPECIFIED = "Not Specified"


class DegreeLevel(str, Enum):
    BACHELORS = "Bachelor's (BS / BA)"
    MASTERS = "Master's (MS / MA)"
    PHD = "PhD / Doctorate"
    ASSOCIATE = "Associate's"
    HIGH_SCHOOL = "High School / Diploma"
    NOT_SPECIFIED = "Not Specified"


class SkillItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = Field(description="Canonical name of the skill or technology (e.g. Python, Distributed Systems, Empathy)")
    category: SkillCategory = Field(description="Category of the skill: technical, soft, tool, or domain")
    proficiency_level: Optional[str] = Field(default=None, description="Proficiency level if mentioned (e.g. Expert, Proficient, Familiar, 3+ years)")
    context_snippet: Optional[str] = Field(default=None, description="Exact sentence or snippet from job description where this skill was mentioned")


class ToolItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = Field(description="Name of specific software, platform, database, or tool (e.g. Docker, AWS, PostgreSQL, Jira, PyTorch)")
    purpose: Optional[str] = Field(default=None, description="Intended purpose or ecosystem (e.g. Containerization, Cloud Infrastructure, Relational DB)")
    is_required: bool = Field(default=True, description="True if mandatory/required, False if preferred/nice-to-have")


class QualificationItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    degree: DegreeLevel = Field(default=DegreeLevel.NOT_SPECIFIED, description="Highest or requested degree level")
    field_of_study: Optional[str] = Field(default=None, description="Relevant field of study (e.g. Computer Science, Data Science, Electrical Engineering)")
    is_required: bool = Field(default=True, description="True if required, False if preferred")
    raw_text: Optional[str] = Field(default=None, description="Exact text snippet regarding education")


class CertificationItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = Field(description="Name of the professional certification (e.g. AWS Certified Solutions Architect, CISSP, CKA, PMP)")
    issuing_body: Optional[str] = Field(default=None, description="Issuing body or vendor (e.g. Amazon Web Services, Linux Foundation, PMI)")
    is_required: bool = Field(default=False, description="True if required, False if preferred or plus")


class ExperienceRequirement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    min_years: Optional[float] = Field(default=None, description="Minimum required years of experience as a number (e.g. 5.0 for 5+ years)")
    max_years: Optional[float] = Field(default=None, description="Maximum years of experience if a range is given (e.g. 8.0 for 5-8 years)")
    seniority_level: SeniorityLevel = Field(default=SeniorityLevel.NOT_SPECIFIED, description="Seniority level inferred or specified")
    domain_area: Optional[str] = Field(default=None, description="Specific domain area for this experience (e.g. Backend distributed systems, NLP, Kubernetes management)")
    raw_text: Optional[str] = Field(default=None, description="Exact text snippet mentioning experience")


class JobPostingExtraction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    job_title: Optional[str] = Field(default=None, description="Job title mentioned in the description")
    seniority_level: SeniorityLevel = Field(default=SeniorityLevel.NOT_SPECIFIED, description="Overall inferred seniority")
    technical_skills: List[SkillItem] = Field(default_factory=list, description="Core technical competencies, programming languages, methodologies, and concepts")
    soft_skills: List[SkillItem] = Field(default_factory=list, description="Interpersonal, leadership, organizational, and collaboration skills")
    tools_and_technologies: List[ToolItem] = Field(default_factory=list, description="Specific tools, platforms, cloud services, and software frameworks")
    qualifications: List[QualificationItem] = Field(default_factory=list, description="Educational requirements and degrees")
    certifications: List[CertificationItem] = Field(default_factory=list, description="Professional certifications and licenses")
    experience_requirements: List[ExperienceRequirement] = Field(default_factory=list, description="Years of experience and domain expertise requirements")
    summary: Optional[str] = Field(default=None, description="Brief 1-2 sentence high-level summary of the candidate profile sought")


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    extraction_method: str = Field(description="Method used: prompt_based, structured_output, rule_based, fine_tuned_sim")
    success: bool = Field(default=True, description="Whether extraction completed and produced valid output")
    extraction: Optional[JobPostingExtraction] = Field(default=None, description="Parsed structured data")
    latency_ms: float = Field(default=0.0, description="Total execution time in milliseconds")
    prompt_tokens: int = Field(default=0, description="Input tokens used")
    completion_tokens: int = Field(default=0, description="Output tokens generated")
    total_tokens: int = Field(default=0, description="Total tokens consumed")
    estimated_cost_usd: float = Field(default=0.0, description="Estimated cost in USD")
    raw_response: str = Field(default="", description="Raw model or system output before parsing")
    is_schema_compliant: bool = Field(default=True, description="Whether the raw output natively adhered to the schema without repairs")
    validation_errors: List[str] = Field(default_factory=list, description="Any validation, parsing, or repair errors encountered")
    notes: Optional[str] = Field(default=None, description="Additional metadata or failure explanations")

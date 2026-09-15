import re
import time
from typing import List, Dict, Set, Tuple, Optional
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


class RuleBasedExtractor(BaseExtractor):
    def __init__(self):
        super().__init__(
            name="rule_based",
            description="High-precision deterministic pattern & dictionary NER extractor",
        )
        self._init_taxonomies()

    def _init_taxonomies(self):
        self.tech_skills_map = {
            "Python": [r"\bpython\b"],
            "Java": [r"\bjava\b(?!script)"],
            "C++": [r"\bc\+\+(?![a-zA-Z0-9+])"],
            "C#": [r"\bc#(?![a-zA-Z0-9#])", r"\bc-sharp\b"],
            "Go (Golang)": [r"\bgolang\b", r"\bgo\s+language\b", r"\bgo\b(?=\s*(?:programming|code|developer|backend))"],
            "Rust": [r"\brust\b(?=\s*(?:programming|developer|systems|code)?)"],
            "TypeScript": [r"\btypescript\b", r"\bts\b(?=\s*(?:developer|code|react))"],
            "JavaScript": [r"\bjavascript\b", r"\bjs\b(?=\s*(?:developer|code|framework))"],
            "SQL": [r"\bsql\b"],
            "Ruby": [r"\bruby\b"],
            "PHP": [r"\bphp\b"],
            "Kotlin": [r"\bkotlin\b"],
            "Swift": [r"\bswift\b"],
            "Scala": [r"\bscala\b"],
            "R": [r"\br\s+programming\b", r"\br\s+language\b", r"\bstatistical\s+r\b"],
            "Distributed Systems": [r"\bdistributed\s+systems?\b", r"\bhigh\s+availability\b", r"\bfault\s+tolerance\b"],
            "Microservices": [r"\bmicroservices?\b", r"\bmicro-services?\b"],
            "RESTful APIs": [r"\brestful?\s*(?:apis?|web\s*services?)\b", r"\brest\s*api\b"],
            "GraphQL": [r"\bgraphql\b"],
            "gRPC": [r"\bgrpc\b"],
            "Event-Driven Architecture": [r"\bevent[- ]driven\b"],
            "Object-Oriented Programming (OOP)": [r"\boop\b", r"\bobject[- ]oriented\b"],
            "CI/CD": [r"\bci[\/-]cd\b", r"\bcontinuous\s+integration\b"],
            "Test-Driven Development (TDD)": [r"\btdd\b", r"\btest[- ]driven\s+development\b"],
            "Data Modeling": [r"\bdata\s+modeling\b", r"\bschema\s+design\b"],
            "Machine Learning": [r"\bmachine\s+learning\b", r"\bml\b(?=\s*(?:models|algorithms|engineering))"],
            "Deep Learning": [r"\bdeep\s+learning\b"],
            "Natural Language Processing (NLP)": [r"\bnlp\b", r"\bnatural\s+language\s+processing\b"],
            "Computer Vision": [r"\bcomputer\s+vision\b"],
            "Large Language Models (LLMs)": [r"\bllms?\b", r"\blarge\s+language\s+models?\b"],
            "Retrieval-Augmented Generation (RAG)": [r"\brag\b", r"\bretrieval[- ]augmented\s+generation\b"],
            "Transformers": [r"\btransformers?\s+architecture\b", r"\bhugging\s*face\b"],
            "Reinforcement Learning": [r"\breinforcement\s+learning\b"],
            "Data Pipelines / ETL": [r"\betl\b", r"\bdata\s+pipelines?\b", r"\bdata\s+ingestion\b"],
            "Concurrency / Multithreading": [r"\bconcurrency\b", r"\bmultithreading\b", r"\basync(?:hronous)?\b"],
            "System Design": [r"\bsystem\s+design\b", r"\bsoftware\s+architecture\b"],
            "Cybersecurity": [r"\bcybersecurity\b", r"\binformation\s+security\b", r"\bpenetration\s+testing\b", r"\bvulnerability\s+assessment\b"],
        }

        self.soft_skills_map = {
            "Communication Skills": [r"\bcommunication(?:\s+skills)?\b", r"\bverbal\s+and\s+written\b", r"\barticulate\b"],
            "Leadership": [r"\bleadership\b", r"\bleading\s+(?:teams?|initiatives?)\b"],
            "Mentorship": [r"\bmentorship\b", r"\bmentoring\b", r"\bcoaching\b"],
            "Collaboration & Teamwork": [r"\bcollaboration\b", r"\bteam\s*player\b", r"\bteamwork\b", r"\bcollaborative\b"],
            "Problem Solving": [r"\bproblem[- ]solving\b", r"\banalytical\s+thinking\b", r"\bcritical\s+thinking\b"],
            "Agile / Scrum": [r"\bagile\b", r"\bscrum\b", r"\bkanban\b", r"\bsprint\b"],
            "Adaptability": [r"\badaptability\b", r"\bflexibility\b", r"\bfast[- ]paced\b"],
            "Stakeholder Management": [r"\bstakeholder\s+management\b", r"\bmanaging\s+stakeholders\b", r"\bcross[- ]functional\b"],
            "Ownership & Accountability": [r"\bownership\b", r"\baccountability\b", r"\bproactive\b", r"\bself[- ]starter\b"],
            "Time Management": [r"\btime\s+management\b", r"\bprioritization\b"],
        }

        self.tools_map = {
            "Docker": ([r"\bdocker\b"], "Containerization"),
            "Kubernetes": ([r"\bkubernetes\b", r"\bk8s\b"], "Container Orchestration"),
            "AWS": ([r"\baws\b", r"\bamazon\s+web\s+services\b"], "Cloud Platform"),
            "Google Cloud Platform (GCP)": ([r"\bgcp\b", r"\bgoogle\s+cloud\b"], "Cloud Platform"),
            "Microsoft Azure": ([r"\bazure\b", r"\bmicrosoft\s+azure\b"], "Cloud Platform"),
            "PostgreSQL": ([r"\bpostgres(?:ql)?\b"], "Relational Database"),
            "MySQL": ([r"\bmysql\b"], "Relational Database"),
            "MongoDB": ([r"\bmongodb\b", r"\bmongo\b"], "NoSQL Database"),
            "Redis": ([r"\bredis\b"], "In-Memory Cache / Key-Value"),
            "Apache Kafka": ([r"\bkafka\b", r"\bapache\s+kafka\b"], "Message Streaming"),
            "RabbitMQ": ([r"\brabbitmq\b"], "Message Broker"),
            "Elasticsearch": ([r"\belasticsearch\b", r"\belk\s+stack\b"], "Search / Analytics Engine"),
            "Snowflake": ([r"\bsnowflake\b"], "Data Cloud / Warehousing"),
            "BigQuery": ([r"\bbigquery\b"], "Data Analytics / Warehousing"),
            "Terraform": ([r"\bterraform\b"], "Infrastructure as Code"),
            "Ansible": ([r"\bansible\b"], "Config Management"),
            "Git": ([r"\bgit\b", r"\bversion\s+control\b"], "Version Control"),
            "GitHub Actions": ([r"\bgithub\s+actions\b"], "CI/CD"),
            "Jenkins": ([r"\bjenkins\b"], "CI/CD"),
            "GitLab CI": ([r"\bgitlab(?:\s+ci)?\b"], "CI/CD"),
            "React": ([r"\breact(?:\.js)?\b"], "Frontend Framework"),
            "Vue.js": ([r"\bvue(?:\.js)?\b"], "Frontend Framework"),
            "Angular": ([r"\bangular\b"], "Frontend Framework"),
            "Next.js": ([r"\bnext(?:\.js)?\b"], "Full-stack Framework"),
            "Node.js": ([r"\bnode(?:\.js)?\b"], "Runtime Environment"),
            "FastAPI": ([r"\bfastapi\b"], "Backend Framework"),
            "Django": ([r"\bdjango\b"], "Backend Framework"),
            "Flask": ([r"\bflask\b"], "Backend Framework"),
            "Spring Boot": ([r"\bspring\s+boot\b", r"\bspring\s+framework\b"], "Java Framework"),
            "PyTorch": ([r"\bpytorch\b"], "Deep Learning Framework"),
            "TensorFlow": ([r"\btensorflow\b"], "Deep Learning Framework"),
            "Scikit-learn": ([r"\bscikit[- ]learn\b", r"\bsklearn\b"], "Machine Learning Library"),
            "Pandas": ([r"\bpandas\b"], "Data Analysis Library"),
            "Apache Spark": ([r"\bapache\s+spark\b", r"\bspark\b(?=\s*(?:streaming|cluster|jobs))"], "Big Data Processing"),
            "Prometheus": ([r"\bprometheus\b"], "Observability / Monitoring"),
            "Grafana": ([r"\bgrafana\b"], "Observability / Dashboards"),
            "Jira": ([r"\bjira\b"], "Project Management"),
            "Linux": ([r"\blinux\b", r"\bunix\b"], "Operating System"),
        }

        self.degree_patterns = [
            (r"\b(ph\.?d|doctorate|doctoral\s+degree)\b", DegreeLevel.PHD),
            (r"\b(master'?s(?:\s+degree)?|m\.?s\.?|m\.?sc\.?|m\.?tech|mba)\b", DegreeLevel.MASTERS),
            (r"\b(bachelor'?s(?:\s+degree)?|b\.?s\.?|b\.?sc\.?|b\.?tech|b\.?a\.?|undergraduate\s+degree)\b", DegreeLevel.BACHELORS),
            (r"\b(associate'?s(?:\s+degree)?|a\.?a\.?|a\.?s\.?)\b", DegreeLevel.ASSOCIATE),
        ]

        self.cert_patterns = [
            (r"\b(aws\s+certified\s+(?:solutions\s+architect|developer|devops\s+engineer|sysops|security))\b", "AWS Certified"),
            (r"\b(cka|certified\s+kubernetes\s+administrator)\b", "Certified Kubernetes Administrator (CKA)"),
            (r"\b(ckad|certified\s+kubernetes\s+application\s+developer)\b", "Certified Kubernetes Application Developer (CKAD)"),
            (r"\b(cissp|certified\s+information\s+systems\s+security\s+professional)\b", "CISSP"),
            (r"\b(pmp|project\s+management\s+professional)\b", "PMP"),
            (r"\b(google\s+cloud\s+(?:certified\s+)?professional\s+cloud\s+architect)\b", "GCP Professional Cloud Architect"),
            (r"\b(microsoft\s+certified(?::\s+azure\s+solutions\s+architect|\s+azure\s+administrator)?)\b", "Microsoft Azure Certified"),
            (r"\b(comptia\s+security\+|security\+\b)\b", "CompTIA Security+"),
            (r"\b(ceh|certified\s+ethical\s+hacker)\b", "Certified Ethical Hacker (CEH)"),
        ]

    def _find_sentence(self, text: str, match_start: int, match_end: int) -> str:
        before = text[:match_start]
        after = text[match_end:]
        start_idx = 0
        for delim in [".", "\n", ";"]:
            pos = before.rfind(delim)
            if pos > start_idx:
                start_idx = pos + 1
        end_idx = len(after)
        for delim in [".", "\n", ";"]:
            pos = after.find(delim)
            if pos != -1 and pos < end_idx:
                end_idx = pos
        snippet = (text[start_idx : match_end + end_idx]).strip()
        return snippet.replace("\r", " ").replace("\n", " ")

    def extract(self, text: str) -> ExtractionResult:
        start_time = time.perf_counter()
        
        extracted_tech: List[SkillItem] = []
        extracted_soft: List[SkillItem] = []
        extracted_tools: List[ToolItem] = []
        extracted_quals: List[QualificationItem] = []
        extracted_certs: List[CertificationItem] = []
        extracted_exp: List[ExperienceRequirement] = []

        seen_tech = set()
        seen_soft = set()
        seen_tools = set()

        for skill_name, patterns in self.tech_skills_map.items():
            for pat in patterns:
                match = re.search(pat, text, re.IGNORECASE)
                if match and skill_name not in seen_tech:
                    seen_tech.add(skill_name)
                    snippet = self._find_sentence(text, match.start(), match.end())
                    extracted_tech.append(
                        SkillItem(
                            name=skill_name,
                            category=SkillCategory.TECHNICAL,
                            context_snippet=snippet[:180] if snippet else None,
                        )
                    )
                    break

        for skill_name, patterns in self.soft_skills_map.items():
            for pat in patterns:
                match = re.search(pat, text, re.IGNORECASE)
                if match and skill_name not in seen_soft:
                    seen_soft.add(skill_name)
                    snippet = self._find_sentence(text, match.start(), match.end())
                    extracted_soft.append(
                        SkillItem(
                            name=skill_name,
                            category=SkillCategory.SOFT,
                            context_snippet=snippet[:180] if snippet else None,
                        )
                    )
                    break

        for tool_name, (patterns, purpose) in self.tools_map.items():
            for pat in patterns:
                match = re.search(pat, text, re.IGNORECASE)
                if match and tool_name not in seen_tools:
                    seen_tools.add(tool_name)
                    is_required = True
                    window = text[max(0, match.start() - 60):min(len(text), match.end() + 60)].lower()
                    if "preferred" in window or "plus" in window or "nice to have" in window or "bonus" in window:
                        is_required = False
                    extracted_tools.append(
                        ToolItem(name=tool_name, purpose=purpose, is_required=is_required)
                    )
                    break

        field_match = re.search(
            r"\bin\s+(Computer Science|Software Engineering|Electrical Engineering|Data Science|Mathematics|Statistics|Information Technology|related\s+field)\b",
            text,
            re.IGNORECASE,
        )
        detected_field = field_match.group(1).title() if field_match else "Computer Science or related field"
        
        seen_degrees = set()
        for pat, degree_enum in self.degree_patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                if degree_enum not in seen_degrees:
                    seen_degrees.add(degree_enum)
                    snippet = self._find_sentence(text, match.start(), match.end())
                    is_required = True
                    if "preferred" in snippet.lower() or "plus" in snippet.lower():
                        is_required = False
                    extracted_quals.append(
                        QualificationItem(
                            degree=degree_enum,
                            field_of_study=detected_field,
                            is_required=is_required,
                            raw_text=snippet[:180],
                        )
                    )

        seen_certs = set()
        for pat, cert_title in self.cert_patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                if cert_title not in seen_certs:
                    seen_certs.add(cert_title)
                    snippet = self._find_sentence(text, match.start(), match.end())
                    is_required = not ("preferred" in snippet.lower() or "plus" in snippet.lower() or "optional" in snippet.lower())
                    extracted_certs.append(
                        CertificationItem(
                            name=cert_title,
                            is_required=is_required,
                        )
                    )

        range_exp_pat = r"(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?(?:\s+(?:in|with)\s+([^,.;\n]+))?"
        for match in re.finditer(range_exp_pat, text, re.IGNORECASE):
            min_y = float(match.group(1))
            max_y = float(match.group(2))
            domain = match.group(3).strip() if match.group(3) else None
            snippet = self._find_sentence(text, match.start(), match.end())
            extracted_exp.append(
                ExperienceRequirement(
                    min_years=min_y,
                    max_years=max_y,
                    domain_area=domain[:80] if domain else "General software / technical experience",
                    raw_text=snippet[:180],
                )
            )

        single_exp_pat = r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+(?:professional\s+)?experience)?(?:\s+(?:in|with)\s+([^,.;\n]+))?"
        if not extracted_exp:
            for match in re.finditer(single_exp_pat, text, re.IGNORECASE):
                min_y = float(match.group(1))
                domain = match.group(2).strip() if match.group(2) else None
                snippet = self._find_sentence(text, match.start(), match.end())
                extracted_exp.append(
                    ExperienceRequirement(
                        min_years=min_y,
                        max_years=None,
                        domain_area=domain[:80] if domain else "General software / technical experience",
                        raw_text=snippet[:180],
                    )
                )

        seniority = SeniorityLevel.NOT_SPECIFIED
        text_lower = text.lower()
        if re.search(r"\b(principal|director|distinguished)\b", text_lower):
            seniority = SeniorityLevel.PRINCIPAL
        elif re.search(r"\b(lead|staff|architect)\b", text_lower) and not re.search(r"\bleadership\b", text_lower) and "lead" in text_lower:
            seniority = SeniorityLevel.LEAD
        elif re.search(r"\b(lead\s+(?:engineer|developer|architect)|staff\s+(?:engineer|developer)|team\s+lead)\b", text_lower):
            seniority = SeniorityLevel.LEAD
        elif re.search(r"\b(senior|sr\.?)\b", text_lower) or (extracted_exp and any(e.min_years and e.min_years >= 5 for e in extracted_exp)):
            seniority = SeniorityLevel.SENIOR
        elif re.search(r"\b(junior|jr\.?|entry|intern|new\s+grad)\b", text_lower):
            seniority = SeniorityLevel.ENTRY
        elif re.search(r"\bmid\b", text_lower) or (extracted_exp and any(e.min_years and e.min_years >= 2 for e in extracted_exp)):
            seniority = SeniorityLevel.MID

        job_title = "Software Professional"
        title_match = re.search(r"^(?:Title:\s*|Job\s*Title:\s*|Position:\s*|Role:\s*)?([^\n]+(?:Engineer|Developer|Architect|Scientist|Specialist|Manager|Analyst|Consultant))", text, re.IGNORECASE | re.MULTILINE)
        if title_match:
            job_title = title_match.group(1).strip()

        extraction_obj = JobPostingExtraction(
            job_title=job_title,
            seniority_level=seniority,
            technical_skills=extracted_tech,
            soft_skills=extracted_soft,
            tools_and_technologies=extracted_tools,
            qualifications=extracted_quals,
            certifications=extracted_certs,
            experience_requirements=extracted_exp,
            summary=f"Extracted {len(extracted_tech)} technical skills, {len(extracted_soft)} soft skills, and {len(extracted_tools)} tools.",
        )

        latency = (time.perf_counter() - start_time) * 1000.0

        return ExtractionResult(
            extraction_method=self.name,
            success=True,
            extraction=extraction_obj,
            latency_ms=round(latency, 2),
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            estimated_cost_usd=0.0,
            raw_response="Rule-based deterministic pattern extraction",
            is_schema_compliant=True,
            validation_errors=[],
            notes="Deterministic local regex & dictionary NER extraction. Zero network latency, $0 token cost.",
        )

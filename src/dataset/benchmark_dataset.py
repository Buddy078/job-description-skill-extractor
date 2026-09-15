from typing import List, Dict, Any, Optional
from ..models.schemas import (
    JobPostingExtraction,
    SkillItem,
    SkillCategory,
    ToolItem,
    QualificationItem,
    DegreeLevel,
    CertificationItem,
    ExperienceRequirement,
    SeniorityLevel,
)

BENCHMARK_DATASET: List[Dict[str, Any]] = [
    {
        "id": "jd_001_backend_go_python",
        "title": "Senior Backend Distributed Systems Engineer",
        "category": "Backend Engineering",
        "raw_text": """Job Title: Senior Backend Engineer
Location: Remote (US / Canada)
About the Role:
We are looking for a Senior Backend Engineer to architect our high-throughput distributed payment processing systems.
You will work closely with cross-functional teams to deliver resilient microservices handling millions of daily transactions.

Requirements:
- 5+ years of software engineering experience building scalable distributed systems.
- Strong proficiency in Python and Go (Golang).
- Practical experience with microservices architecture, RESTful APIs, and gRPC.
- Hands-on experience with Docker, Kubernetes, and AWS cloud infrastructure.
- Solid database fundamentals with PostgreSQL and Redis caching.
- Experience with Apache Kafka for event-driven streaming.
- Strong problem-solving skills, ownership mindset, and excellent verbal and written communication skills.

Qualifications:
- Bachelor's degree in Computer Science, Software Engineering, or equivalent experience.
- Preferred: Master's degree in Computer Science.
- Nice to have: AWS Certified Solutions Architect.
""",
        "ground_truth": JobPostingExtraction(
            job_title="Senior Backend Engineer",
            seniority_level=SeniorityLevel.SENIOR,
            technical_skills=[
                SkillItem(name="Python", category=SkillCategory.TECHNICAL),
                SkillItem(name="Go (Golang)", category=SkillCategory.TECHNICAL),
                SkillItem(name="Distributed Systems", category=SkillCategory.TECHNICAL),
                SkillItem(name="Microservices", category=SkillCategory.TECHNICAL),
                SkillItem(name="RESTful APIs", category=SkillCategory.TECHNICAL),
                SkillItem(name="gRPC", category=SkillCategory.TECHNICAL),
                SkillItem(name="Event-Driven Architecture", category=SkillCategory.TECHNICAL),
            ],
            soft_skills=[
                SkillItem(name="Problem Solving", category=SkillCategory.SOFT),
                SkillItem(name="Ownership & Accountability", category=SkillCategory.SOFT),
                SkillItem(name="Communication Skills", category=SkillCategory.SOFT),
                SkillItem(name="Collaboration & Teamwork", category=SkillCategory.SOFT),
            ],
            tools_and_technologies=[
                ToolItem(name="Docker", purpose="Containerization", is_required=True),
                ToolItem(name="Kubernetes", purpose="Container Orchestration", is_required=True),
                ToolItem(name="AWS", purpose="Cloud Platform", is_required=True),
                ToolItem(name="PostgreSQL", purpose="Relational Database", is_required=True),
                ToolItem(name="Redis", purpose="In-Memory Cache", is_required=True),
                ToolItem(name="Apache Kafka", purpose="Message Streaming", is_required=True),
            ],
            qualifications=[
                QualificationItem(degree=DegreeLevel.BACHELORS, field_of_study="Computer Science", is_required=True),
                QualificationItem(degree=DegreeLevel.MASTERS, field_of_study="Computer Science", is_required=False),
            ],
            certifications=[
                CertificationItem(name="AWS Certified Solutions Architect", is_required=False),
            ],
            experience_requirements=[
                ExperienceRequirement(min_years=5.0, domain_area="scalable distributed systems", seniority_level=SeniorityLevel.SENIOR),
            ],
            summary="Seeking a Senior Backend Engineer with 5+ years building distributed systems in Python and Go.",
        ),
    },
    {
        "id": "jd_002_ml_rag_engineer",
        "title": "Staff Machine Learning Engineer (LLMs & RAG)",
        "category": "AI / Machine Learning",
        "raw_text": """Position: Staff Machine Learning Engineer - GenAI
Location: San Francisco, CA (Hybrid)

Responsibilities:
Lead the research and deployment of enterprise Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) pipelines.
You will train, fine-tune, and evaluate deep learning models and guide junior engineers through technical mentorship.

Qualifications & Experience:
- 7+ years of hands-on Machine Learning and Deep Learning experience.
- Deep expertise in Natural Language Processing (NLP), Transformers, and PyTorch.
- Experience productionizing ML models with FastAPI, Docker, and Kubernetes on Google Cloud Platform (GCP).
- Master's degree or PhD in Computer Science, Data Science, or Artificial Intelligence required.
- Proven leadership and mentorship track record with cross-functional stakeholder management.
- Strong proficiency in Python and SQL.
""",
        "ground_truth": JobPostingExtraction(
            job_title="Staff Machine Learning Engineer - GenAI",
            seniority_level=SeniorityLevel.LEAD,
            technical_skills=[
                SkillItem(name="Machine Learning", category=SkillCategory.TECHNICAL),
                SkillItem(name="Deep Learning", category=SkillCategory.TECHNICAL),
                SkillItem(name="Large Language Models (LLMs)", category=SkillCategory.TECHNICAL),
                SkillItem(name="Retrieval-Augmented Generation (RAG)", category=SkillCategory.TECHNICAL),
                SkillItem(name="Natural Language Processing (NLP)", category=SkillCategory.TECHNICAL),
                SkillItem(name="Transformers", category=SkillCategory.TECHNICAL),
                SkillItem(name="Python", category=SkillCategory.TECHNICAL),
                SkillItem(name="SQL", category=SkillCategory.TECHNICAL),
            ],
            soft_skills=[
                SkillItem(name="Leadership", category=SkillCategory.SOFT),
                SkillItem(name="Mentorship", category=SkillCategory.SOFT),
                SkillItem(name="Stakeholder Management", category=SkillCategory.SOFT),
            ],
            tools_and_technologies=[
                ToolItem(name="PyTorch", purpose="Deep Learning Framework", is_required=True),
                ToolItem(name="FastAPI", purpose="Backend Framework", is_required=True),
                ToolItem(name="Docker", purpose="Containerization", is_required=True),
                ToolItem(name="Kubernetes", purpose="Container Orchestration", is_required=True),
                ToolItem(name="Google Cloud Platform (GCP)", purpose="Cloud Platform", is_required=True),
            ],
            qualifications=[
                QualificationItem(degree=DegreeLevel.PHD, field_of_study="Computer Science or AI", is_required=True),
                QualificationItem(degree=DegreeLevel.MASTERS, field_of_study="Computer Science or AI", is_required=True),
            ],
            certifications=[],
            experience_requirements=[
                ExperienceRequirement(min_years=7.0, domain_area="Machine Learning and Deep Learning", seniority_level=SeniorityLevel.LEAD),
            ],
            summary="Staff ML Engineer to build production LLM and RAG pipelines using PyTorch, GCP, and Kubernetes.",
        ),
    },
    {
        "id": "jd_003_cloud_devops_architect",
        "title": "Principal Cloud DevOps & Infrastructure Architect",
        "category": "Cloud & DevOps",
        "raw_text": """Role: Principal Cloud DevOps Architect
We are seeking a seasoned Principal Cloud DevOps Architect to define our multi-cloud infrastructure strategy across AWS and Microsoft Azure.

What You Bring:
- 10+ years of experience in infrastructure architecture and site reliability engineering.
- Mastery of Infrastructure as Code (IaC) using Terraform and Ansible.
- Extensive experience managing enterprise Kubernetes clusters and GitOps with GitLab CI and GitHub Actions.
- In-depth understanding of Cybersecurity best practices and compliance.
- Certifications Required: CISSP or Certified Kubernetes Administrator (CKA).
- Excellent executive communication and strategic leadership skills.
- Bachelor's degree in Computer Science or Information Technology.
""",
        "ground_truth": JobPostingExtraction(
            job_title="Principal Cloud DevOps Architect",
            seniority_level=SeniorityLevel.PRINCIPAL,
            technical_skills=[
                SkillItem(name="System Design", category=SkillCategory.TECHNICAL),
                SkillItem(name="CI/CD", category=SkillCategory.TECHNICAL),
                SkillItem(name="Cybersecurity", category=SkillCategory.TECHNICAL),
            ],
            soft_skills=[
                SkillItem(name="Leadership", category=SkillCategory.SOFT),
                SkillItem(name="Communication Skills", category=SkillCategory.SOFT),
            ],
            tools_and_technologies=[
                ToolItem(name="AWS", purpose="Cloud Platform", is_required=True),
                ToolItem(name="Microsoft Azure", purpose="Cloud Platform", is_required=True),
                ToolItem(name="Terraform", purpose="Infrastructure as Code", is_required=True),
                ToolItem(name="Ansible", purpose="Config Management", is_required=True),
                ToolItem(name="Kubernetes", purpose="Container Orchestration", is_required=True),
                ToolItem(name="GitLab CI", purpose="CI/CD", is_required=True),
                ToolItem(name="GitHub Actions", purpose="CI/CD", is_required=True),
            ],
            qualifications=[
                QualificationItem(degree=DegreeLevel.BACHELORS, field_of_study="Computer Science or IT", is_required=True),
            ],
            certifications=[
                CertificationItem(name="CISSP", is_required=True),
                CertificationItem(name="Certified Kubernetes Administrator (CKA)", is_required=True),
            ],
            experience_requirements=[
                ExperienceRequirement(min_years=10.0, domain_area="infrastructure architecture and SRE", seniority_level=SeniorityLevel.PRINCIPAL),
            ],
            summary="Principal Cloud Architect to oversee multi-cloud IaC, Kubernetes clusters, and security governance.",
        ),
    },
    {
        "id": "jd_004_fullstack_react_node",
        "title": "Senior Full Stack Engineer (React, TypeScript & Node.js)",
        "category": "Full Stack",
        "raw_text": """Job Title: Senior Full Stack Engineer
Join our product engineering group! We are looking for an experienced Full Stack Engineer who loves creating responsive, high-performance web applications.

Skills Needed:
- 4 to 6 years of professional web development experience.
- Expert knowledge of TypeScript, JavaScript, React, and Next.js.
- Strong backend experience with Node.js and RESTful APIs or GraphQL.
- Proficiency with PostgreSQL and MongoDB.
- Familiarity with Docker and Git version control.
- Experience working in an Agile / Scrum team environment.
- Bachelor's in Computer Science or related degree.
""",
        "ground_truth": JobPostingExtraction(
            job_title="Senior Full Stack Engineer",
            seniority_level=SeniorityLevel.SENIOR,
            technical_skills=[
                SkillItem(name="TypeScript", category=SkillCategory.TECHNICAL),
                SkillItem(name="JavaScript", category=SkillCategory.TECHNICAL),
                SkillItem(name="RESTful APIs", category=SkillCategory.TECHNICAL),
                SkillItem(name="GraphQL", category=SkillCategory.TECHNICAL),
            ],
            soft_skills=[
                SkillItem(name="Agile / Scrum", category=SkillCategory.SOFT),
                SkillItem(name="Collaboration & Teamwork", category=SkillCategory.SOFT),
            ],
            tools_and_technologies=[
                ToolItem(name="React", purpose="Frontend Framework", is_required=True),
                ToolItem(name="Next.js", purpose="Full-stack Framework", is_required=True),
                ToolItem(name="Node.js", purpose="Runtime Environment", is_required=True),
                ToolItem(name="PostgreSQL", purpose="Relational Database", is_required=True),
                ToolItem(name="MongoDB", purpose="NoSQL Database", is_required=True),
                ToolItem(name="Docker", purpose="Containerization", is_required=True),
                ToolItem(name="Git", purpose="Version Control", is_required=True),
            ],
            qualifications=[
                QualificationItem(degree=DegreeLevel.BACHELORS, field_of_study="Computer Science or related field", is_required=True),
            ],
            certifications=[],
            experience_requirements=[
                ExperienceRequirement(min_years=4.0, max_years=6.0, domain_area="professional web development", seniority_level=SeniorityLevel.SENIOR),
            ],
            summary="Full stack engineer with 4-6 years in React, TypeScript, Next.js, and Node.js with PostgreSQL.",
        ),
    },
    {
        "id": "jd_005_data_scientist_bigdata",
        "title": "Lead Data Scientist (Spark, Snowflake & Analytics)",
        "category": "Data Science",
        "raw_text": """Position: Lead Data Scientist
We are hiring a Lead Data Scientist to build predictive models and large-scale data pipelines.

Requirements:
- 6+ years of data science and analytics experience.
- Deep expertise with Python, SQL, and statistical modeling.
- Solid background in machine learning with Scikit-learn and Pandas.
- Experience with big data processing using Apache Spark.
- Experience with cloud data warehouses like Snowflake and BigQuery.
- Master's degree in Statistics, Mathematics, Data Science, or Computer Science.
- Excellent stakeholder management and analytical problem-solving skills.
""",
        "ground_truth": JobPostingExtraction(
            job_title="Lead Data Scientist",
            seniority_level=SeniorityLevel.LEAD,
            technical_skills=[
                SkillItem(name="Python", category=SkillCategory.TECHNICAL),
                SkillItem(name="SQL", category=SkillCategory.TECHNICAL),
                SkillItem(name="Machine Learning", category=SkillCategory.TECHNICAL),
                SkillItem(name="Data Pipelines / ETL", category=SkillCategory.TECHNICAL),
            ],
            soft_skills=[
                SkillItem(name="Problem Solving", category=SkillCategory.SOFT),
                SkillItem(name="Stakeholder Management", category=SkillCategory.SOFT),
            ],
            tools_and_technologies=[
                ToolItem(name="Scikit-learn", purpose="ML Library", is_required=True),
                ToolItem(name="Pandas", purpose="Data Analysis Library", is_required=True),
                ToolItem(name="Apache Spark", purpose="Big Data Processing", is_required=True),
                ToolItem(name="Snowflake", purpose="Data Cloud", is_required=True),
                ToolItem(name="BigQuery", purpose="Data Analytics", is_required=True),
            ],
            qualifications=[
                QualificationItem(degree=DegreeLevel.MASTERS, field_of_study="Statistics, Mathematics, or Data Science", is_required=True),
            ],
            certifications=[],
            experience_requirements=[
                ExperienceRequirement(min_years=6.0, domain_area="data science and analytics", seniority_level=SeniorityLevel.LEAD),
            ],
            summary="Lead Data Scientist proficient in Spark, Snowflake, Scikit-learn, and statistical analysis.",
        ),
    },
]


def get_all_benchmark_jobs() -> List[Dict[str, Any]]:
    return BENCHMARK_DATASET


def get_benchmark_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    for job in BENCHMARK_DATASET:
        if job["id"] == job_id:
            return job
    return None

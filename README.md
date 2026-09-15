# Job Description Skill & Information Extractor

A modular, production-grade information-extraction pipeline that identifies:
- **Technical Skills**: Programming languages, distributed systems, architectures, methodologies
- **Soft Skills**: Collaboration, leadership, communication, problem-solving, stakeholder management
- **Tools & Technologies**: Cloud platforms (AWS, GCP, Azure), databases, containers, CI/CD tools
- **Qualifications**: Degrees (Bachelor's, Master's, PhD), fields of study, required vs preferred
- **Certifications**: Professional licenses (AWS Solutions Architect, CKA, CISSP, PMP)
- **Experience Requirements**: Minimum and maximum years, seniority level, domain area

---

## 🔬 Approaches Compared

| Feature / Metric | Prompt-Based (Unconstrained JSON) | Structured-Output (Gemini Schema) | Local Rule-Based NER | Fine-Tuned Model (Simulated) |
| :--- | :--- | :--- | :--- | :--- |
| **Model Type** | Gemini 3.8 Flash (Few-shot text prompt) | Gemini 3.8 Flash (`response_format` JSON schema) | High-Precision Regex & Lexicon NER | Fine-tuned 8B sequence model / tagger |
| **Schema Adherence** | ⚠️ Variable (fences, preamble, key drift) | ✅ **100% Guaranteed** (Grammar-constrained) | ✅ **100% Guaranteed** | ✅ **100% Guaranteed** |
| **Parsing Repair Needed?**| Yes (Markdown backticks, missing keys) | **No (Direct Pydantic validation)** | **No** | **No** |
| **Inference Latency** | ~500 - 1,500 ms | ~400 - 1,200 ms | **~2 - 10 ms (Instant)** | ~40 - 80 ms |
| **Token Cost** | ~$0.55 / 1,000 JDs | ~$0.50 / 1,000 JDs | **$0.00 (Zero)** | **$0.00 (Self-hosted)** |
| **Offline Operation** | No (Requires API connection) | No (Requires API connection) | **Yes (100% Offline)** | **Yes (100% Offline)** |
| **Domain Generalization** | High (Captures unseen terms) | High (Captures unseen terms) | Medium (Requires dictionary update) | High on trained domains |

---

## 🚀 Quickstart

### 1. Installation
Clone or navigate to the repository:
```powershell
cd "C:\Users\rogith.k\.gemini\antigravity\scratch\job-description-skill-extractor"
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
If you wish to run live Gemini API calls, configure your API key in a `.env` file or environment variable:
```powershell
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
```
> **Note**: If no API key is provided, the pipeline seamlessly operates in **Offline Mode** with instant local rule-based NER and synthetic benchmark evaluations.

---

## 💻 CLI Usage

### Extract from text or file
```powershell
# Extract using Schema-Enforced Structured Output
python -m src.cli extract --text "Senior Python Developer with 5+ years in Docker, Kubernetes, and AWS." --method structured

# Run all 4 approaches side-by-side on a file
python -m src.cli extract --file sample_jd.txt --method all

# Export extracted output as clean JSON
python -m src.cli extract --text "Frontend Lead with React and TypeScript." --method rule --json
```

### Run Evaluation Benchmarks
Run the evaluation harness comparing all 4 approaches across the ground-truth benchmark suite:
```powershell
python -m src.cli benchmark --output reports/benchmark.json
```

### Export Fine-Tuning Datasets
Convert ground-truth annotated job descriptions into fine-tuning datasets:
```powershell
# Export Gemini / OpenAI Chat SFT format
python -m src.cli export-dataset --format chat --output data/finetune_chat.jsonl

# Export Alpaca / HuggingFace instruction format
python -m src.cli export-dataset --format instruction --output data/finetune_alpaca.jsonl

# Export Token-level BIO tagging NER format
python -m src.cli export-dataset --format bio --output data/finetune_bio.json
```

---

## 🖥️ Streamlit Interactive Dashboard

Launch the web dashboard:
```powershell
streamlit run src/ui/app.py
```
The dashboard provides 4 interactive tabs:
1. **Live Playground**: Test single or custom JDs with badge rendering, experience gauges, and JSON inspection.
2. **Head-to-Head Comparison**: Real-time side-by-side diff comparing prompt-based vs structured output.
3. **Benchmark & Evaluation**: One-click benchmark runner with interactive Altair charts for F1, compliance, and cost.
4. **Fine-Tuning Hub**: Inspect annotated records, view color-coded token BIO sequences, and export fine-tuning data.

---

## 🧪 Automated Tests

Run the full pytest suite:
```powershell
pytest tests/ -v
```
All 15 unit tests verify schemas, normalization, extractors, benchmark datasets, and evaluation metrics.

TO START: 
cd "C:\Users\rogith.k\Desktop\job-description-skill-extractor"
.\.venv\Scripts\Activate.ps1
python -m streamlit run src/ui/app.py

TO START FIRST TIME:
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# 1. Run all unit & integration tests
python -m pytest tests/ -v

# 2. Run the benchmark tool
python -m src.cli benchmark
python -m streamlit run src/ui/app.py

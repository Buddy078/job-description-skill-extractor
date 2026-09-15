import os
import json
import time
import html
import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv

from src.extractors.rule_based import RuleBasedExtractor
from src.extractors.prompt_based import PromptBasedExtractor
from src.extractors.structured_output import StructuredOutputExtractor
from src.extractors.fine_tuned_sim import FineTunedModelSimulator
from src.evaluation.comparator import PipelineComparator
from src.dataset.benchmark_dataset import BENCHMARK_DATASET, get_all_benchmark_jobs
from src.dataset.fine_tuning_generator import FineTuningDataGenerator

load_dotenv()

st.set_page_config(
    page_title="Job Description Skill Extractor",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_badge_chips(items, badge_type: str = "tech") -> str:
    """Safely renders a collection of entity items as an inline flex container of chips.
    Guarantees zero unescaped tags or broken quotes by escaping text and attributes.
    """
    if not items:
        return "<p style='color: #888; font-size: 0.88rem; font-style: italic; margin-top: 4px;'>None detected</p>"

    chips_html = []
    for item in items:
        if hasattr(item, "name"):
            name = item.name
            if hasattr(item, "is_required"):
                req_text = "Req" if item.is_required else "Plus"
                label = f"{name} ({req_text})"
            else:
                label = name

            tooltip_parts = []
            if getattr(item, "proficiency_level", None):
                tooltip_parts.append(f"Level: {item.proficiency_level}")
            if getattr(item, "purpose", None):
                tooltip_parts.append(f"Purpose: {item.purpose}")
            if getattr(item, "context_snippet", None):
                clean_snippet = str(item.context_snippet).replace("\r", " ").replace("\n", " ").strip()
                if len(clean_snippet) > 180:
                    clean_snippet = clean_snippet[:177] + "..."
                tooltip_parts.append(f"Context: {clean_snippet}")
            tooltip = " | ".join(tooltip_parts)
        else:
            label = str(item)
            tooltip = ""

        safe_label = html.escape(str(label))
        safe_title = ""
        if tooltip:
            safe_title = f' title="{html.escape(tooltip, quote=True)}"'

        chips_html.append(f'<span class="custom-chip chip-{badge_type}"{safe_title}>{safe_label}</span>')

    return f'<div class="chip-container">{"".join(chips_html)}</div>'


# Custom CSS styling (supports both Dark and Light mode automatically)
st.markdown("""
<style>
    .metric-card {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 6px;
        margin-bottom: 16px;
    }
    .custom-chip {
        display: inline-flex;
        align-items: center;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.86rem;
        font-weight: 500;
        cursor: default;
        line-height: 1.4;
        transition: transform 0.1s ease;
    }
    .custom-chip:hover {
        transform: translateY(-1px);
    }
    /* Technical skills - Cyan / Blue */
    .chip-tech {
        background-color: rgba(2, 132, 199, 0.18);
        color: #0284c7;
        border: 1px solid rgba(2, 132, 199, 0.4);
    }
    /* Soft skills - Violet / Purple */
    .chip-soft {
        background-color: rgba(147, 51, 234, 0.18);
        color: #9333ea;
        border: 1px solid rgba(147, 51, 234, 0.4);
    }
    /* Tools - Green / Emerald */
    .chip-tool {
        background-color: rgba(22, 163, 74, 0.18);
        color: #16a34a;
        border: 1px solid rgba(22, 163, 74, 0.4);
    }
    /* Certifications - Amber / Orange */
    .chip-cert {
        background-color: rgba(234, 88, 12, 0.18);
        color: #ea580c;
        border: 1px solid rgba(234, 88, 12, 0.4);
    }

    /* Dark mode enhancements */
    @media (prefers-color-scheme: dark) {
        .chip-tech { color: #38bdf8; background-color: rgba(2, 132, 199, 0.25); border-color: rgba(56, 189, 248, 0.5); }
        .chip-soft { color: #c084fc; background-color: rgba(147, 51, 234, 0.25); border-color: rgba(192, 132, 252, 0.5); }
        .chip-tool { color: #4ade80; background-color: rgba(22, 163, 74, 0.25); border-color: rgba(74, 222, 128, 0.5); }
        .chip-cert { color: #fb923c; background-color: rgba(234, 88, 12, 0.25); border-color: rgba(251, 146, 60, 0.5); }
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar settings
st.sidebar.title("⚙️ Configuration")
env_api_key = os.environ.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Gemini API Key (Optional)", value=env_api_key, type="password", help="Leave blank to run in offline high-speed mode using rule-based and local simulators.")

if api_key and api_key.strip():
    st.sidebar.success("🔑 Gemini API Key Active (gemini-3.8-flash)")
else:
    st.sidebar.info("\u26A1 Offline Mode Active (Zero network latency, $0 cost, deterministic extraction)")

model_choice = st.sidebar.selectbox("LLM Model", ["gemini-3.8-flash", "gemini-3.5-flash-lite"], index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📌 Extraction Taxonomy
- **Technical Skills**: Architecture, languages, methods
- **Soft Skills**: Collaboration, leadership, communication
- **Tools & Tech**: Platforms, DBs, cloud services
- **Qualifications**: Education & degree requirements
- **Certifications**: Industry licenses & certs
- **Experience**: Years of experience & seniority
""")

st.title("💼 Job Description Skill & Information Extractor")
st.markdown("Extract technical skills, soft skills, tools, qualifications, and experience from unstructured job descriptions. Compare **Prompt-Based**, **Structured-Output (Gemini JSON Schema)**, and **Local Rule-Based NER**.")

tabs = st.tabs([
    "🎯 Live Playground",
    "⚖️ Head-to-Head Comparison",
    "📊 Benchmark & Evaluation",
    "🧪 Fine-Tuning & Dataset Hub",
])

# ----------------- TAB 1: Live Playground -----------------
with tabs[0]:
    st.subheader("Interactive Extraction Playground")
    col_input, col_config = st.columns([3, 1])

    with col_config:
        preset_options = ["Custom Input"] + [f"{j['id']}: {j['title']}" for j in BENCHMARK_DATASET]
        selected_preset = st.selectbox("Load Sample Job Description", preset_options)
        
        extractor_choice = st.selectbox(
            "Extraction Method",
            ["Structured-Output (Schema-Enforced)", "Prompt-Based (Natural Language)", "Rule-Based NER (Local)", "Fine-Tuned Model (Simulated)"]
        )

    # Preset text logic
    default_text = ""
    if selected_preset != "Custom Input":
        selected_id = selected_preset.split(":")[0]
        for job in BENCHMARK_DATASET:
            if job["id"] == selected_id:
                default_text = job["raw_text"]
                break
    else:
        default_text = """Job Title: Senior Cloud Backend Engineer
Location: Remote
We are seeking a Senior Backend Engineer with 5+ years of experience in distributed systems.
Requirements:
- 5+ years of hands-on experience in Python and Go (Golang).
- Strong proficiency with Docker, Kubernetes, and AWS cloud infrastructure.
- Solid experience with PostgreSQL, Redis, and Apache Kafka.
- Proven leadership, teamwork, and strong verbal communication skills.
- Bachelor's degree in Computer Science or Software Engineering.
- Preferred: AWS Certified Solutions Architect.
"""

    with col_input:
        jd_input = st.text_area("Job Description Text", value=default_text, height=220)

    if st.button("🚀 Run Extraction", type="primary", use_container_width=True):
        if not jd_input.strip():
            st.error("Please enter a job description to extract information.")
        else:
            with st.spinner("Extracting structured information..."):
                if "Structured-Output" in extractor_choice:
                    extractor = StructuredOutputExtractor(api_key=api_key)
                elif "Prompt-Based" in extractor_choice:
                    extractor = PromptBasedExtractor(api_key=api_key)
                elif "Rule-Based" in extractor_choice:
                    extractor = RuleBasedExtractor()
                else:
                    extractor = FineTunedModelSimulator()

                res = extractor.extract(jd_input)

            # Display metrics row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Status", "Success" if res.success else "Failed")
            m2.metric("Schema Compliant", "Yes (100%)" if res.is_schema_compliant else "No (Repaired)")
            m3.metric("Latency", f"{res.latency_ms:.1f} ms")
            m4.metric("Est. Cost", f"${res.estimated_cost_usd:.5f}" if res.estimated_cost_usd > 0 else "$0.00 (Local)")

            if res.validation_errors:
                with st.expander("⚠️ Validation Warnings & Repairs", expanded=True):
                    for err in res.validation_errors:
                        st.warning(err)

            if res.extraction:
                ext = res.extraction
                st.markdown("---")
                
                # Header info
                h1, h2, h3 = st.columns(3)
                h1.markdown(f"**Job Title:** {ext.job_title or 'Not specified'}")
                h2.markdown(f"**Seniority Level:** `{ext.seniority_level.value}`")
                h3.markdown(f"**Summary:** {ext.summary or 'N/A'}")

                # Entities in columns
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### 💻 Technical Skills")
                    st.markdown(render_badge_chips(ext.technical_skills, "tech"), unsafe_allow_html=True)

                    st.markdown("#### 🛠️ Tools & Technologies")
                    st.markdown(render_badge_chips(ext.tools_and_technologies, "tool"), unsafe_allow_html=True)

                    st.markdown("#### 📜 Certifications")
                    st.markdown(render_badge_chips(ext.certifications, "cert"), unsafe_allow_html=True)

                with c2:
                    st.markdown("#### 🤝 Soft Skills")
                    st.markdown(render_badge_chips(ext.soft_skills, "soft"), unsafe_allow_html=True)

                    st.markdown("#### 🎓 Qualifications & Degrees")
                    if ext.qualifications:
                        for q in ext.qualifications:
                            req_txt = "Required" if q.is_required else "Preferred"
                            st.info(f"**{q.degree.value}** in *{q.field_of_study or 'Related field'}* ({req_txt})")
                    else:
                        st.caption("No explicit degree specified.")

                    st.markdown("#### ⏳ Experience Requirements")
                    if ext.experience_requirements:
                        for exp in ext.experience_requirements:
                            years_str = f"{exp.min_years}+ years" if exp.min_years else "Experience specified"
                            if exp.min_years and exp.max_years:
                                years_str = f"{exp.min_years} - {exp.max_years} years"
                            st.success(f"**{years_str}** | Domain: *{exp.domain_area or 'General'}*")
                    else:
                        st.caption("No specific years requirement found.")

                # Citations and Context Snippets Expander
                evidence_items = [s for s in ext.technical_skills if s.context_snippet]
                if evidence_items:
                    with st.expander("📌 View Skill Evidence & Context Citations"):
                        for s in evidence_items:
                            clean_snip = str(s.context_snippet).replace("\r", " ").replace("\n", " ").strip()
                            st.markdown(f"- **{s.name}**: *\"{clean_snip}\"*")

                with st.expander("🔍 View Raw JSON Output"):
                    st.json(ext.model_dump())

# ----------------- TAB 2: Head-to-Head Comparison -----------------
with tabs[1]:
    st.subheader("Side-by-Side Method Comparison")
    st.markdown("Compare extraction performance, latency, token consumption, and schema adherence across approaches on the same job description.")

    compare_text = st.text_area("Input Job Description for Comparison", value=default_text, height=180, key="compare_input")

    if st.button("⚡ Run Comparative Analysis", type="primary"):
        with st.spinner("Executing extraction across all 4 pipelines..."):
            comparator = PipelineComparator(api_key=api_key)
            results = comparator.compare_single_text(compare_text)

        # Overview Table
        summary_rows = []
        for name, data in results.items():
            r = data["result"]
            summary_rows.append({
                "Pipeline": name,
                "Success": "✅ Yes" if r.success else "❌ No",
                "Schema Adherence": "100% Guaranteed" if r.is_schema_compliant else "⚠️ Repaired Markdown Fences",
                "Latency (ms)": r.latency_ms,
                "Total Tokens": r.total_tokens,
                "Cost ($)": f"${r.estimated_cost_usd:.5f}",
                "Tech Skills": len(r.extraction.technical_skills) if r.extraction else 0,
                "Soft Skills": len(r.extraction.soft_skills) if r.extraction else 0,
                "Tools": len(r.extraction.tools_and_technologies) if r.extraction else 0,
            })

        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### 🔬 Entity Extraction Comparison")
        cols = st.columns(len(results))
        for i, (name, data) in enumerate(results.items()):
            with cols[i]:
                st.markdown(f"**{name}**")
                r = data["result"]
                if r.extraction:
                    st.caption(f"Title: {r.extraction.job_title}")
                    st.markdown("**Technical Skills:**")
                    st.write(", ".join([s.name for s in r.extraction.technical_skills]) or "None")
                    st.markdown("**Soft Skills:**")
                    st.write(", ".join([s.name for s in r.extraction.soft_skills]) or "None")
                    st.markdown("**Tools:**")
                    st.write(", ".join([t.name for t in r.extraction.tools_and_technologies]) or "None")
                    st.markdown("**Qualifications:**")
                    st.write(", ".join([q.degree.value for q in r.extraction.qualifications]) or "None")
                    st.markdown("**Experience:**")
                    st.write(", ".join([f"{e.min_years}+ yrs" for e in r.extraction.experience_requirements if e.min_years]) or "None")
                if r.validation_errors:
                    st.error(f"Format issues: {len(r.validation_errors)}")

# ----------------- TAB 3: Benchmark & Evaluation -----------------
with tabs[2]:
    st.subheader("Gold-Standard Benchmark Evaluation")
    st.markdown("Evaluate pipelines across the 5 human-annotated ground-truth job postings. Measures Precision, Recall, F1 scores, schema adherence rates, latency, and token cost.")

    if st.button("📊 Run Benchmark Suite", type="primary"):
        with st.spinner("Benchmarking all pipelines against ground truth..."):
            comparator = PipelineComparator(api_key=api_key)
            bench_df = comparator.run_benchmark_suite()
            st.session_state["benchmark_results"] = bench_df

    if "benchmark_results" in st.session_state:
        df = st.session_state["benchmark_results"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("### 📈 Visual Comparative Charts")
        c1, c2 = st.columns(2)

        with c1:
            chart_f1 = alt.Chart(df).mark_bar().encode(
                x=alt.X("Method:N", title="Pipeline"),
                y=alt.Y("Overall F1 Score:Q", title="Overall F1 Score", scale=alt.Scale(domain=[0.8, 1.0])),
                color=alt.Color("Method:N", legend=None),
            ).properties(title="Overall F1 Score by Method", height=280)
            st.altair_chart(chart_f1, use_container_width=True)

        with c2:
            chart_compliance = alt.Chart(df).mark_bar().encode(
                x=alt.X("Method:N", title="Pipeline"),
                y=alt.Y("Schema Compliance Rate (%):Q", title="Schema Compliance (%)", scale=alt.Scale(domain=[0, 105])),
                color=alt.Color("Method:N", legend=None),
            ).properties(title="Native Schema Compliance Rate (%)", height=280)
            st.altair_chart(chart_compliance, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            chart_latency = alt.Chart(df).mark_bar().encode(
                x=alt.X("Method:N", title="Pipeline"),
                y=alt.Y("Avg Latency (ms):Q", title="Average Latency (ms)"),
                color=alt.Color("Method:N", legend=None),
            ).properties(title="Inference Latency (ms)", height=280)
            st.altair_chart(chart_latency, use_container_width=True)

        with c4:
            chart_cost = alt.Chart(df).mark_bar().encode(
                x=alt.X("Method:N", title="Pipeline"),
                y=alt.Y("Est. Cost / 1k JDs ($):Q", title="Cost per 1,000 JDs ($)"),
                color=alt.Color("Method:N", legend=None),
            ).properties(title="Cost per 1,000 Job Descriptions ($)", height=280)
            st.altair_chart(chart_cost, use_container_width=True)

# ----------------- TAB 4: Fine-Tuning & Dataset Hub -----------------
with tabs[3]:
    st.subheader("Fine-Tuning Dataset Generator & BIO Tag Viewer")
    st.markdown("Explore ground-truth training records and export fine-tuning datasets formatted for **Gemini / OpenAI SFT**, **HuggingFace / Alpaca**, or **BIO Token Classification**.")

    gen = FineTuningDataGenerator()

    hub_col1, hub_col2 = st.columns([1, 1])

    with hub_col1:
        st.markdown("#### 📂 Export Fine-Tuning Datasets")
        format_sel = st.selectbox("Export Format", ["Chat JSONL (Gemini / OpenAI)", "Instruction JSONL (Alpaca / HuggingFace)", "BIO Token Sequence (NER)"])
        
        fmt_map = {
            "Chat JSONL (Gemini / OpenAI)": "chat",
            "Instruction JSONL (Alpaca / HuggingFace)": "instruction",
            "BIO Token Sequence (NER)": "bio",
        }
        
        if st.button("💾 Export Dataset File"):
            fmt = fmt_map[format_sel]
            ext = "jsonl" if fmt != "bio" else "json"
            out_file = f"data/finetune_export_{fmt}.{ext}"
            saved_path = gen.export_to_file(out_file, format_type=fmt)
            st.success(f"Exported {len(BENCHMARK_DATASET)} records to `{saved_path}`!")

    with hub_col2:
        st.markdown("#### 🏷️ BIO Token Sequence Preview")
        bio_docs = gen.generate_bio_tagged_tokens()
        doc_idx = st.selectbox("Select Annotated Job", range(len(bio_docs)), format_func=lambda i: f"Job {i+1}: {BENCHMARK_DATASET[i]['title']}")
        
        doc = bio_docs[doc_idx]
        tagged_pairs = [(t, tag) for t, tag in zip(doc["tokens"], doc["bio_tags"]) if tag != "O"]
        st.markdown(f"**Identified Entities ({len(tagged_pairs)} tagged tokens):**")
        st.dataframe(pd.DataFrame(tagged_pairs, columns=["Token", "BIO Tag"]), height=250, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📋 Inspect Ground-Truth Annotated Records")
    for item in BENCHMARK_DATASET:
        with st.expander(f"{item['id']}: {item['title']} ({item['category']})"):
            st.markdown("**Raw Job Description:**")
            st.text(item["raw_text"])
            st.markdown("**Annotated Ground Truth:**")
            st.json(item["ground_truth"].model_dump())

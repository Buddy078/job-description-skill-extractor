import re

app_path = r'C:\Users\rogith.k\.gemini\antigravity\scratch\job-description-skill-extractor\src\ui\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    code = f.read()

replacements = [
    ('page_icon="??"', 'page_icon="\U0001F4BC"'),
    ('st.sidebar.title("?? Configuration")', 'st.sidebar.title("\u2699\uFE0F Configuration")'),
    ('st.sidebar.success("?? Gemini API Key Active (gemini-3.8-flash)")', 'st.sidebar.success("\U0001F511 Gemini API Key Active (gemini-3.8-flash)")'),
    ('st.sidebar.info("? Offline Mode Active (Zero network latency,  cost, deterministic extraction)")', 'st.sidebar.info("\u26A1 Offline Mode Active (Zero network latency,  cost, deterministic extraction)")'),
    ('### ?? Extraction Taxonomy', '### \U0001F4CC Extraction Taxonomy'),
    ('st.title("?? Job Description Skill & Information Extractor")', 'st.title("\U0001F4BC Job Description Skill & Information Extractor")'),
    ('"?? Live Playground"', '"\U0001F3AF Live Playground"'),
    ('"?? Head-to-Head Comparison"', '"\u2696\uFE0F Head-to-Head Comparison"'),
    ('"?? Benchmark & Evaluation"', '"\U0001F4CA Benchmark & Evaluation"'),
    ('"?? Fine-Tuning & Dataset Hub"', '"\U0001F9EA Fine-Tuning & Dataset Hub"'),
    ('st.button("?? Run Extraction"', 'st.button("\U0001F680 Run Extraction"'),
    ('with st.expander("?? Validation Warnings & Repairs"', 'with st.expander("\u26A0\uFE0F Validation Warnings & Repairs"'),
    ('st.markdown("#### ?? Technical Skills")', 'st.markdown("#### \U0001F4BB Technical Skills")'),
    ('st.markdown("#### ??? Tools & Technologies")', 'st.markdown("#### \U0001F6E0\uFE0F Tools & Technologies")'),
    ('req_badge = "? Req" if t.is_required else "? Plus"', 'req_badge = "Required" if t.is_required else "Preferred"'),
    ('st.markdown("#### ?? Certifications")', 'st.markdown("#### \U0001F4DC Certifications")'),
    ('st.markdown("#### ?? Soft Skills")', 'st.markdown("#### \U0001F91D Soft Skills")'),
    ('st.markdown("#### ?? Qualifications & Degrees")', 'st.markdown("#### \U0001F393 Qualifications & Degrees")'),
    ('st.markdown("#### ? Experience Requirements")', 'st.markdown("#### \u23F3 Experience Requirements")'),
    ('with st.expander("?? View Raw JSON Output")', 'with st.expander("\U0001F50D View Raw JSON Output"'),
    ('st.button("? Run Comparative Analysis"', 'st.button("\u26A1 Run Comparative Analysis"'),
    ('"Success": "? Yes" if r.success else "? No"', '"Success": "\u2705 Yes" if r.success else "\u274C No"'),
    ('"Schema Adherence": "100% Guaranteed" if r.is_schema_compliant else "?? Markdown / Format Errors"', '"Schema Adherence": "100% Guaranteed" if r.is_schema_compliant else "\u26A0\uFE0F Repaired Markdown Fences"'),
    ('st.markdown("### ?? Entity Extraction Comparison")', 'st.markdown("### \U0001F52C Entity Extraction Comparison")'),
    ('st.button("?? Run Benchmark Suite"', 'st.button("\U0001F4CA Run Benchmark Suite"'),
    ('st.markdown("### ?? Visual Comparative Charts")', 'st.markdown("### \U0001F4C8 Visual Comparative Charts")'),
    ('st.markdown("#### ?? Export Fine-Tuning Datasets")', 'st.markdown("#### \U0001F4C2 Export Fine-Tuning Datasets")'),
    ('st.button("?? Export Dataset File")', 'st.button("\U0001F4BE Export Dataset File")'),
    ('st.markdown("#### ??? BIO Token Sequence Preview")', 'st.markdown("#### \U0001F3F7\uFE0F BIO Token Sequence Preview")'),
    ('st.markdown("#### ?? Inspect Ground-Truth Annotated Records")', 'st.markdown("#### \U0001F4CB Inspect Ground-Truth Annotated Records")'),
]

count = 0
for old, new in replacements:
    if old in code:
        code = code.replace(old, new)
        count += 1
    else:
        print(f"Not found: {old}")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(code)

print(f"Updated app.py with {count} fixes!")

# Also fix README.md
readme_path = r'C:\Users\rogith.k\.gemini\antigravity\scratch\job-description-skill-extractor\README.md'
with open(readme_path, 'r', encoding='utf-8') as f:
    readme = f.read()

readme_replacements = [
    ('## ?? Approaches Compared', '## \U0001F52C Approaches Compared'),
    ('| **Schema Adherence** | ?? Variable (fences, preamble, key drift) | ??? **100% Guaranteed** (Grammar-constrained) | ??? **100% Guaranteed** | ??? **100% Guaranteed** |',
     '| **Schema Adherence** | \u26A0\uFE0F Variable (fences, preamble, key drift) | \u2705 **100% Guaranteed** (Grammar-constrained) | \u2705 **100% Guaranteed** | \u2705 **100% Guaranteed** |'),
    ('## ?? Quickstart', '## \U0001F680 Quickstart'),
    ('## ?? CLI Usage', '## \U0001F4BB CLI Usage'),
    ('## ??? Streamlit Interactive Dashboard', '## \U0001F5A5\uFE0F Streamlit Interactive Dashboard'),
    ('## ?? Automated Tests', '## \U0001F9EA Automated Tests'),
]

r_count = 0
for old, new in readme_replacements:
    if old in readme:
        readme = readme.replace(old, new)
        r_count += 1
    else:
        print(f"README Not found: {old}")

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(readme)

print(f"Updated README.md with {r_count} fixes!")
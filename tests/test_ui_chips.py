from src.extractors.rule_based import RuleBasedExtractor
from src.ui.app import render_badge_chips

def test_chips_rendering():
    text = '''Job Title: Senior Cloud Backend Engineer
Requirements:
- 5+ years of hands-on experience in Python and Go (Golang).
- Strong proficiency with Docker, Kubernetes, and AWS cloud infrastructure.
'''
    extractor = RuleBasedExtractor()
    res = extractor.extract(text)
    tech_html = render_badge_chips(res.extraction.technical_skills, 'tech')
    assert '\n' not in tech_html
    assert 'custom-chip chip-tech' in tech_html
    assert 'Python' in tech_html

    empty_html = render_badge_chips([], 'tech')
    assert 'None detected' in empty_html
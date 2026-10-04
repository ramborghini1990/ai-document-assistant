"""
Streamlit UI styling, KPI cards injection, and safe HTML escaping.
"""
import html
import streamlit as st

_CSS = """
<style>
:root {
    --glass: rgba(255, 255, 255, 0.04);
    --glass-border: rgba(255, 255, 255, 0.10);
    --accent: #4ADE80;
    --radius: 12px;
}
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
    max-width: 1440px;
}
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 1.2rem;
}
.kpi-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 14px 16px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}
.kpi-card.warn {
    border-color: rgba(250, 204, 21, 0.6);
    background: rgba(250, 204, 21, 0.05);
}
.kpi-card.crit {
    border-color: rgba(248, 113, 113, 0.7);
    background: rgba(248, 113, 113, 0.08);
}
.kpi-label {
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    opacity: 0.75;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1.1;
    color: #FFFFFF;
}
.kpi-hint {
    font-size: 0.75rem;
    opacity: 0.55;
    margin-top: 4px;
}
div[data-testid="stExpander"] {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
}
.stButton > button, .stDownloadButton > button {
    border-radius: 8px;
    font-weight: 600;
}
</style>
"""


def inject_custom_css() -> None:
    """تزریق استایل شیشه‌ای (Glassmorphism) و بهینه‌سازی فاصله‌ها."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_kpi_row(items: list) -> None:
    """
    نمایش ردیف کارت‌های آماری KPI با پاک‌سازی امن HTML.
    items: [(label, value, hint, level)]
    level: '' (عادی), 'warn' (هشدار زرد), 'crit' (بحرانی قرمز)
    """
    cards = "".join(
        f'<div class="kpi-card {html.escape(lv)}">'
        f'<div class="kpi-label">{html.escape(str(lb))}</div>'
        f'<div class="kpi-value">{html.escape(str(v))}</div>'
        f'<div class="kpi-hint">{html.escape(str(h))}</div>'
        f'</div>'
        for lb, v, h, lv in items
    )
    st.markdown(f'<div class="kpi-grid">{cards}</div>', unsafe_allow_html=True)
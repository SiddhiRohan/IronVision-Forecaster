import streamlit as st
import json
import plotly.graph_objects as go
import os
from datetime import datetime

st.set_page_config(
    page_title="IronVision | Site Intelligence",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════
# FULL THEME — IronVision Construction Intelligence
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

    /* ── Reset & Base ── */
    .stApp {
        background: #08090C;
        color: #E2E0DB;
    }
    #MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] { display: none !important; }
    * { font-family: 'Plus Jakarta Sans', sans-serif !important; }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #08090C; }
    ::-webkit-scrollbar-thumb { background: #E8912D; border-radius: 10px; }

    /* ── Typography ── */
    h1, h2, h3 { color: #F0EFEB !important; letter-spacing: -0.03em; }
    h1 { font-weight: 800 !important; }
    h2 { font-weight: 700 !important; font-size: 1.15rem !important; }
    p, span, li, div, label { color: #9B9890; }

    hr { border-color: rgba(255,255,255,0.04) !important; margin: 2rem 0 !important; }

    /* ── Hero Banner ── */
    .hero-banner {
        position: relative;
        background: #08090C;
        border-radius: 20px;
        padding: 44px 48px 40px;
        margin-bottom: 28px;
        border: 1px solid rgba(255,255,255,0.06);
        overflow: hidden;
        z-index: 1;
    }
    .hero-video {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        object-fit: cover;
        opacity: 0.25;
        z-index: -1;
        border-radius: 20px;
    }
    .hero-overlay {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(8,9,12,0.85) 0%, rgba(8,9,12,0.6) 50%, rgba(8,9,12,0.9) 100%);
        z-index: -1;
        border-radius: 20px;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #E8912D 20%, #F5A623 50%, #E8912D 80%, transparent);
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: 0; right: 0;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(232,145,45,0.06) 0%, transparent 70%);
        pointer-events: none;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 6px;
    }
    .brand-icon {
        width: 42px; height: 42px;
        background: linear-gradient(135deg, #E8912D, #F5A623);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        box-shadow: 0 4px 20px rgba(232,145,45,0.3);
    }
    .brand-name {
        font-size: 1.6rem;
        font-weight: 800;
        color: #F0EFEB !important;
        letter-spacing: -0.03em;
    }
    .brand-name em {
        font-style: normal;
        color: #F5A623 !important;
    }
    .hero-subtitle {
        color: #6B6860;
        font-size: 0.88rem;
        font-weight: 400;
        margin-top: 2px;
        letter-spacing: 0.02em;
    }

    .hero-meta-row {
        display: flex;
        gap: 24px;
        margin-top: 20px;
        flex-wrap: wrap;
    }
    .hero-chip {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 8px;
        padding: 7px 14px;
        font-size: 0.78rem;
        color: #B8B5AE !important;
        font-weight: 500;
    }
    .hero-chip .chip-icon { font-size: 0.85rem; }
    .hero-chip .chip-val { color: #F0EFEB !important; font-weight: 600; }

    /* ── Metric Cards ── */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.02);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 22px 26px;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: linear-gradient(135deg, rgba(232,145,45,0.03) 0%, transparent 60%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(232,145,45,0.3);
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3), 0 0 20px rgba(232,145,45,0.05);
    }
    [data-testid="stMetric"]:hover::before { opacity: 1; }

    [data-testid="stMetric"] label {
        color: #5A5850 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.65rem !important;
        letter-spacing: 0.14em;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #F0EFEB !important;
        font-weight: 800 !important;
        font-size: 1.7rem !important;
        font-family: 'Space Mono', monospace !important;
    }

    /* ── Glass Cards ── */
    .glass-card {
        background: rgba(255,255,255,0.02);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 28px 30px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        position: relative;
    }
    .glass-card:hover {
        border-color: rgba(255,255,255,0.1);
        box-shadow: 0 8px 40px rgba(0,0,0,0.2);
    }
    .glass-card h2 {
        margin-top: 0 !important;
        padding-top: 0 !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-icon {
        width: 32px; height: 32px;
        background: rgba(232,145,45,0.1);
        border: 1px solid rgba(232,145,45,0.2);
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
    }

    /* ── Narrative Box ── */
    .narrative-box {
        background: rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 22px;
        font-size: 0.9rem;
        line-height: 1.8;
        color: #B8B5AE !important;
        position: relative;
    }
    .narrative-box::before {
        content: '"';
        position: absolute;
        top: 10px; left: 16px;
        font-size: 3rem;
        color: rgba(232,145,45,0.15);
        font-family: Georgia, serif;
        line-height: 1;
    }

    /* ── Task Cards ── */
    .task-card {
        background: rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.04);
        border-left: 3px solid #E8912D;
        border-radius: 0 12px 12px 0;
        padding: 18px 22px;
        margin-bottom: 10px;
        transition: all 0.25s ease;
    }
    .task-card:hover {
        background: rgba(232,145,45,0.04);
        border-left-color: #F5A623;
        transform: translateX(4px);
    }
    .task-header { display: flex; justify-content: space-between; align-items: center; }
    .task-name { color: #F0EFEB !important; font-weight: 600; font-size: 0.92rem; }
    .task-badge {
        font-family: 'Space Mono', monospace !important;
        background: rgba(232,145,45,0.1);
        color: #F5A623 !important;
        font-size: 0.68rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 6px;
        border: 1px solid rgba(232,145,45,0.2);
    }
    .task-action { color: #8A8780 !important; font-size: 0.83rem; margin-top: 8px; line-height: 1.5; }

    /* ── Material Items ── */
    .mat-item {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 14px 18px;
        background: rgba(0,0,0,0.25);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 12px;
        margin-bottom: 8px;
        transition: all 0.25s ease;
    }
    .mat-item:hover {
        border-color: rgba(232,145,45,0.2);
        background: rgba(232,145,45,0.03);
    }
    .mat-qty-wrap {
        min-width: 70px;
        text-align: center;
    }
    .mat-qty {
        font-family: 'Space Mono', monospace !important;
        color: #F5A623 !important;
        font-weight: 700;
        font-size: 1.4rem;
        line-height: 1;
    }
    .mat-unit {
        font-family: 'Space Mono', monospace !important;
        color: #5A5850 !important;
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .mat-info { flex: 1; }
    .mat-name { color: #E2E0DB !important; font-weight: 600; font-size: 0.88rem; }
    .mat-note {
        color: #4A4840 !important;
        font-size: 0.72rem;
        font-family: 'Space Mono', monospace !important;
        margin-top: 3px;
        line-height: 1.4;
    }

    /* ── Observed Task Pill ── */
    .obs-task {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 11px 16px;
        background: rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 10px;
        margin-bottom: 6px;
        transition: all 0.2s ease;
    }
    .obs-task:hover { border-color: rgba(255,255,255,0.08); }
    .obs-task-name { color: #E2E0DB !important; font-weight: 500; font-size: 0.85rem; }
    .obs-conf {
        font-family: 'Space Mono', monospace !important;
        font-size: 0.65rem;
        color: #5A5850 !important;
        letter-spacing: 0.05em;
    }
    .conf-fill {
        color: #F5A623 !important;
    }

    /* ── Risk / Rec Items ── */
    .risk-item {
        padding: 14px 18px;
        background: rgba(229, 62, 62, 0.04);
        border: 1px solid rgba(229, 62, 62, 0.1);
        border-left: 3px solid #E53E3E;
        border-radius: 0 10px 10px 0;
        margin-bottom: 8px;
        color: #D4D2CD !important;
        font-size: 0.86rem;
        transition: all 0.2s ease;
    }
    .risk-item:hover { background: rgba(229, 62, 62, 0.07); transform: translateX(3px); }

    .rec-item {
        padding: 14px 18px;
        background: rgba(72, 187, 120, 0.04);
        border: 1px solid rgba(72, 187, 120, 0.1);
        border-left: 3px solid #48BB78;
        border-radius: 0 10px 10px 0;
        margin-bottom: 8px;
        color: #D4D2CD !important;
        font-size: 0.86rem;
        transition: all 0.2s ease;
    }
    .rec-item:hover { background: rgba(72, 187, 120, 0.07); transform: translateX(3px); }

    /* ── Status Dot ── */
    .status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        margin-right: 6px;
        vertical-align: middle;
    }
    .dot-green { background: #48BB78; box-shadow: 0 0 8px rgba(72,187,120,0.4); }
    .dot-amber { background: #F5A623; box-shadow: 0 0 8px rgba(245,166,35,0.4); }
    .dot-red { background: #E53E3E; box-shadow: 0 0 8px rgba(229,62,62,0.4); }
    .dot-gray { background: #3A3830; }

    /* ── Alerts ── */
    .stAlert { border-radius: 10px !important; }

    /* ── Plotly bg ── */
    .js-plotly-plot .plotly .bg { fill: transparent !important; }

    /* ── Footer ── */
    .iv-footer {
        text-align: center;
        padding: 32px 20px 20px;
        border-top: 1px solid rgba(255,255,255,0.04);
        margin-top: 40px;
    }
    .iv-footer-brand {
        font-weight: 800;
        font-size: 0.9rem;
        color: #F5A623 !important;
        letter-spacing: -0.02em;
    }
    .iv-footer-sub {
        color: #2A2820 !important;
        font-size: 0.7rem;
        font-family: 'Space Mono', monospace !important;
        margin-top: 6px;
        letter-spacing: 0.03em;
    }

    /* ── Streamlit overrides ── */
    .stExpander { border: none !important; }
    div[data-testid="stExpander"] details {
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        background: rgba(255,255,255,0.02) !important;
    }
    div[data-testid="stExpander"] summary {
        color: #E2E0DB !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════
def load_json(path):
    with open(path) as f:
        return json.load(f)

data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
if os.path.exists(os.path.join(data_dir, "output", "video_summary.json")):
    data_path = os.path.join(data_dir, "output")
else:
    data_path = os.path.join(data_dir, "mock")

blueprint = load_json(os.path.join(os.path.dirname(__file__), "..", "blueprint.json"))
summary = load_json(os.path.join(data_path, "video_summary.json"))
prediction = load_json(os.path.join(data_path, "prediction.json"))

progress = prediction["current_progress"]
plan = prediction["next_day_plan"]


# ═══════════════════════════════════════════════════════════
# HERO BANNER
# ═══════════════════════════════════════════════════════════
crew = summary['summary'].get('crew_size_observed', 'N/A')
weather = summary['summary'].get('weather_conditions', '')


st.markdown(f"""
<div class="hero-banner">
    <video class="hero-video" autoplay muted loop playsinline>
        <source src="app/static/bg.mp4" type="video/mp4">
    </video>
    <div class="hero-overlay"></div>
    <div style="text-align:center; margin-bottom:8px;">
        <div class="brand-icon" style="margin:0 auto 12px;">◆</div>
        <div class="brand-name" style="font-size:2.2rem;">Iron<em>Vision</em></div>
        <div class="hero-subtitle">AI-Powered Construction Forecast Report</div>
    </div>
    <div class="hero-meta-row" style="justify-content:center;">
        <div class="hero-chip">
            <span class="chip-icon">📐</span>
            <span class="chip-val">{blueprint['project_name']}</span>
        </div>
        <div class="hero-chip">
            <span class="chip-icon">📅</span>
            <span class="chip-val">{summary['date']}</span>
        </div>
        <div class="hero-chip">
            <span class="chip-icon">👷</span>
            <span class="chip-val">{crew} crew on site</span>
        </div>
        {'<div class="hero-chip"><span class="chip-icon">🌤️</span><span class="chip-val">' + weather + '</span></div>' if weather else ''}
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# METRIC CARDS
# ═══════════════════════════════════════════════════════════
c1, c2 = st.columns(2)

with c1:
    st.metric("OVERALL PROGRESS", f"{progress['overall_percent_complete']}%")
with c2:
    st.metric("EST. COMPLETION", plan.get("estimated_completion_date", "TBD"))

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# PROGRESS CHART + SITE REPORT
# ═══════════════════════════════════════════════════════════
left, right = st.columns([3, 2])

with left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2><span class="section-icon">📊</span> Construction Progress</h2>', unsafe_allow_html=True)

    steps_data = []
    for step in blueprint["steps"]:
        sid = step["step_id"]
        if sid in progress.get("completed_steps", []):
            pct, color, label, dot = 100, "#48BB78", "COMPLETE", "dot-green"
        elif any(s["step_id"] == sid for s in progress.get("in_progress_steps", [])):
            ip = next(s for s in progress["in_progress_steps"] if s["step_id"] == sid)
            pct = ip["percent_complete"]
            color, label, dot = "#F5A623", f"{pct}%", "dot-amber"
        else:
            pct, color, label, dot = 0, "#1E222A", "PENDING", "dot-gray"
        steps_data.append({
            "name": f"  {step['name'][:34]}",
            "pct": pct, "color": color, "label": label, "dot": dot
        })

    fig = go.Figure()

    # Track bars
    fig.add_trace(go.Bar(
        y=[d["name"] for d in steps_data],
        x=[100] * len(steps_data),
        orientation='h',
        marker_color='rgba(255,255,255,0.03)',
        showlegend=False, hoverinfo='skip'
    ))

    # Progress bars
    fig.add_trace(go.Bar(
        y=[d["name"] for d in steps_data],
        x=[d["pct"] for d in steps_data],
        orientation='h',
        marker_color=[d["color"] for d in steps_data],
        marker_line=dict(width=0),
        text=[d["label"] for d in steps_data],
        textposition="inside",
        textfont=dict(family="Space Mono", size=11, color="#08090C"),
        showlegend=False,
        hovertemplate="%{y}<br>Progress: %{x}%<extra></extra>"
    ))

    fig.update_layout(
        barmode='overlay',
        xaxis=dict(range=[0, 100], showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(family="Plus Jakarta Sans", size=12, color="#9B9890")
        ),
        height=50 + len(steps_data) * 52,
        margin=dict(l=10, r=20, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        bargap=0.35
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


with right:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2><span class="section-icon">📝</span> Site Report</h2>', unsafe_allow_html=True)

    narrative = summary["summary"].get("overall_narrative", "No summary available.")
    st.markdown(f'<div class="narrative-box">{narrative}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Tasks observed
    tasks_obs = summary["summary"].get("tasks_observed", [])
    if tasks_obs:
        st.markdown("<p style='color:#6B6860; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:8px;'>Tasks Detected</p>", unsafe_allow_html=True)
        for t in tasks_obs:
            conf = t.get('confidence', 0)
            filled = int(conf * 10)
            conf_bar = f"<span class='conf-fill'>{'●' * filled}</span>{'○' * (10 - filled)}"
            icon = "✅" if t.get("status") == "completed" else "🔨" if t.get("status") == "in_progress" else "⏳"
            dot = "dot-green" if t.get("status") == "completed" else "dot-amber" if t.get("status") == "in_progress" else "dot-gray"
            st.markdown(f"""
            <div class="obs-task">
                <span class="obs-task-name"><span class="status-dot {dot}"></span>{t.get('task', 'Unknown')}</span>
                <span class="obs-conf">{conf_bar} {conf:.0%}</span>
            </div>
            """, unsafe_allow_html=True)

    issues = summary["summary"].get("issues_or_blockers", [])
    if issues:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("<p style='color:#6B6860; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:8px;'>⚠️ Issues Flagged</p>", unsafe_allow_html=True)
        for issue in issues:
            st.markdown(f'<div class="risk-item" style="border-left-color:#F5A623; background:rgba(245,166,35,0.04); border-color:rgba(245,166,35,0.1);">{issue}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# TOMORROW'S PLAN + MATERIALS
# ═══════════════════════════════════════════════════════════
left2, right2 = st.columns([3, 2])

with left2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2><span class="section-icon">📅</span> Next Day Plan</h2>', unsafe_allow_html=True)

    for i, task in enumerate(plan.get("priority_tasks", [])):
        hrs = task.get('estimated_hours', '?')
        crew_n = task.get('crew_needed', '?')
        st.markdown(f"""
        <div class="task-card">
            <div class="task-header">
                <span class="task-name">{'🔸' if i == 0 else '▪️'} {task.get('task', 'Unknown Task')}</span>
                <span class="task-badge">{hrs}h · {crew_n} crew</span>
            </div>
            <div class="task-action">{task.get('action', '')}</div>
        </div>
        """, unsafe_allow_html=True)

    # Total hours summary
    total_hrs = sum(t.get('estimated_hours', 0) for t in plan.get("priority_tasks", []))
    total_crew = max((t.get('crew_needed', 0) for t in plan.get("priority_tasks", [])), default=0)
    st.markdown(f"""
    <div style="display:flex; gap:20px; margin-top:14px; padding:12px 0;">
        <div style="font-family:'Space Mono',monospace; font-size:0.72rem;">
            <span style="color:#5A5850;">TOTAL HOURS</span>
            <span style="color:#F5A623; font-weight:700; margin-left:8px;">{total_hrs:.1f}h</span>
        </div>
        <div style="font-family:'Space Mono',monospace; font-size:0.72rem;">
            <span style="color:#5A5850;">PEAK CREW</span>
            <span style="color:#F5A623; font-weight:700; margin-left:8px;">{total_crew}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2><span class="section-icon">📦</span> Materials Required</h2>', unsafe_allow_html=True)

    for mat in plan.get("materials_needed_tomorrow", []):
        note = mat.get('note', '')
        st.markdown(f"""
        <div class="mat-item">
            <div class="mat-qty-wrap">
                <div class="mat-qty">{mat.get('quantity', '?')}</div>
                <div class="mat-unit">{mat.get('unit', '')}</div>
            </div>
            <div class="mat-info">
                <div class="mat-name">{mat.get('name', 'Unknown')}</div>
                {'<div class="mat-note">' + note + '</div>' if note else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# RISKS + RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════
left3, right3 = st.columns(2)

with left3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2><span class="section-icon">🚧</span> Risk Assessment</h2>', unsafe_allow_html=True)

    risks = plan.get("risks", [])
    if risks:
        for risk in risks:
            st.markdown(f'<div class="risk-item"><span class="status-dot dot-red"></span>{risk}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#3A3830; padding:12px;">No risks identified</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<h2><span class="section-icon">💡</span> Recommendations</h2>', unsafe_allow_html=True)

    recs = prediction.get("recommendations", [])
    if recs:
        for rec in recs:
            st.markdown(f'<div class="rec-item"><span class="status-dot dot-green"></span>{rec}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#3A3830; padding:12px;">No recommendations</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
gen_time = prediction.get('generated_at', 'N/A')
st.markdown(f"""
<div class="iv-footer">
    <div class="iv-footer-brand">Iron<span style="color:#F5A623">Vision</span></div>
    <div class="iv-footer-sub">
        AI-POWERED SITE INTELLIGENCE · VIDEO ANALYSIS · PREDICTIVE PLANNING<br>
        Generated {gen_time}
    </div>
</div>
""", unsafe_allow_html=True)

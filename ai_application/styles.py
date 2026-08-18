"""
Premium CSS styles for the Banking AI Application.
Dark theme with glassmorphism, gradients, and micro-animations.
"""


def get_custom_css() -> str:
    return """
<style>
    /* ─── Google Font ──────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ─── Global ───────────────────────────────────────────────── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ─── Sidebar ──────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1B2A 0%, #1B2838 50%, #0D1B2A 100%);
        border-right: 1px solid rgba(0, 180, 216, 0.15);
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #E0E1DD !important;
        font-weight: 500;
        padding: 6px 0;
        transition: all 0.3s ease;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        color: #00B4D8 !important;
        padding-left: 8px;
    }
    .sidebar-section-title {
        font-size: 0.78rem;
        font-weight: 800;
        color: #E0E1DD;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-top: 20px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .sidebar-status-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 10px;
        background: rgba(13, 27, 42, 0.6);
        border: 1px solid rgba(0, 180, 216, 0.12);
        border-radius: 8px;
        margin-bottom: 6px;
        font-size: 0.82rem;
        color: #E0E1DD;
    }
    .sidebar-status-badge {
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .sidebar-status-badge.connected, .sidebar-status-badge.active {
        color: #06D6A0;
    }
    .sidebar-status-badge.disconnected, .sidebar-status-badge.missing {
        color: #E63946;
    }
    .tech-stack-container {
        display: flex;
        flex-direction: column;
        gap: 5px;
        padding: 4px 0;
    }
    .tech-stack-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(27, 40, 56, 0.6);
        border: 1px solid rgba(0, 180, 216, 0.12);
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 0.78rem;
        color: #E0E1DD;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .tech-stack-item:hover {
        border-color: rgba(0, 180, 216, 0.35);
        background: rgba(0, 180, 216, 0.08);
        transform: translateX(3px);
    }
    .voice-control-box {
        background: linear-gradient(135deg, rgba(0,180,216,0.12), rgba(46,196,182,0.06));
        border: 1.5px solid rgba(0,180,216,0.4);
        border-radius: 14px;
        padding: 16px;
        margin-top: 16px;
        margin-bottom: 12px;
    }

    /* ─── Header Area ──────────────────────────────────────────── */
    .main-header {
        background: linear-gradient(135deg, #0D1B2A 0%, #1B2838 50%, #0D1B2A 100%);
        border: 1px solid rgba(0, 180, 216, 0.2);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(0,180,216,0.06) 0%, transparent 60%);
        animation: headerGlow 8s ease-in-out infinite;
    }
    @keyframes headerGlow {
        0%, 100% { transform: translate(0, 0); }
        50% { transform: translate(20px, -10px); }
    }
    .main-header h1 {
        color: #E0E1DD;
        font-weight: 800;
        font-size: 2rem;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    .main-header p {
        color: #778DA9;
        font-size: 1rem;
        margin-top: 6px;
        position: relative;
        z-index: 1;
    }

    /* ─── Metric Cards ─────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, rgba(27,40,56,0.9) 0%, rgba(13,27,42,0.95) 100%);
        border: 1px solid rgba(0,180,216,0.15);
        border-radius: 14px;
        padding: 22px 20px;
        text-align: center;
        transition: all 0.35s cubic-bezier(.4,0,.2,1);
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        border-color: rgba(0,180,216,0.45);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,180,216,0.12);
    }
    .metric-card .metric-icon {
        font-size: 2rem;
        margin-bottom: 6px;
    }
    .metric-card .metric-value {
        font-size: 1.7rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00B4D8, #2EC4B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 4px 0;
    }
    .metric-card .metric-label {
        font-size: 0.82rem;
        color: #778DA9;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    /* Gold variant */
    .metric-card.gold .metric-value {
        background: linear-gradient(135deg, #FFB703, #FB5607);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card.gold:hover {
        border-color: rgba(255,183,3,0.45);
        box-shadow: 0 12px 40px rgba(255,183,3,0.12);
    }

    /* Purple variant */
    .metric-card.purple .metric-value {
        background: linear-gradient(135deg, #7B2CBF, #E63946);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card.purple:hover {
        border-color: rgba(123,44,191,0.45);
        box-shadow: 0 12px 40px rgba(123,44,191,0.12);
    }

    /* Green variant */
    .metric-card.green .metric-value {
        background: linear-gradient(135deg, #06D6A0, #2EC4B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card.green:hover {
        border-color: rgba(6,214,160,0.45);
        box-shadow: 0 12px 40px rgba(6,214,160,0.12);
    }

    /* ─── Glass Panel ──────────────────────────────────────────── */
    .glass-panel {
        background: rgba(13, 27, 42, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0,180,216,0.12);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 16px;
    }

    /* ─── Chat Bubbles ─────────────────────────────────────────── */
    .chat-user {
        background: linear-gradient(135deg, #1B2838, #0D1B2A);
        border: 1px solid rgba(0,180,216,0.2);
        border-radius: 16px 16px 4px 16px;
        padding: 16px 20px;
        margin: 10px 0;
        color: #E0E1DD;
        animation: slideInRight 0.4s ease;
        max-width: 85%;
        margin-left: auto;
    }
    .chat-agent {
        background: linear-gradient(135deg, rgba(0,180,216,0.08), rgba(46,196,182,0.06));
        border: 1px solid rgba(0,180,216,0.2);
        border-radius: 16px 16px 16px 4px;
        padding: 16px 20px;
        margin: 10px 0;
        color: #E0E1DD;
        animation: slideInLeft 0.4s ease;
        max-width: 85%;
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    /* ─── Agent Badge ──────────────────────────────────────────── */
    .agent-badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 8px;
    }
    .agent-badge.support { background: rgba(46,196,182,0.15); color: #2EC4B6; border: 1px solid rgba(46,196,182,0.3); }
    .agent-badge.data    { background: rgba(0,180,216,0.15);  color: #00B4D8; border: 1px solid rgba(0,180,216,0.3); }
    .agent-badge.ml      { background: rgba(123,44,191,0.15); color: #7B2CBF; border: 1px solid rgba(123,44,191,0.3); }

    /* ─── Section Title ────────────────────────────────────────── */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #E0E1DD;
        margin-bottom: 14px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(0,180,216,0.2);
        display: inline-block;
    }

    /* ─── Status Indicator ─────────────────────────────────────── */
    .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s ease-in-out infinite;
    }
    .status-dot.active { background: #06D6A0; box-shadow: 0 0 8px rgba(6,214,160,0.5); }
    .status-dot.inactive { background: #E63946; box-shadow: 0 0 8px rgba(230,57,70,0.5); }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* ─── Architecture Box ─────────────────────────────────────── */
    .arch-box {
        background: linear-gradient(135deg, rgba(0,180,216,0.06), rgba(123,44,191,0.06));
        border: 1px solid rgba(0,180,216,0.15);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .arch-box:hover {
        border-color: rgba(0,180,216,0.4);
        box-shadow: 0 8px 30px rgba(0,180,216,0.08);
    }
    .arch-box .arch-icon { font-size: 2rem; margin-bottom: 6px; }
    .arch-box .arch-title { font-weight: 700; color: #E0E1DD; font-size: 0.9rem; }
    .arch-box .arch-desc  { color: #778DA9; font-size: 0.78rem; margin-top: 4px; }

    /* ─── Divider ──────────────────────────────────────────────── */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0,180,216,0.4), rgba(123,44,191,0.4), transparent);
        border: none;
        margin: 24px 0;
        border-radius: 2px;
    }

    /* ─── Report Card ──────────────────────────────────────────── */
    .report-card {
        background: linear-gradient(135deg, rgba(27,40,56,0.9), rgba(13,27,42,0.95));
        border: 1px solid rgba(0,180,216,0.12);
        border-radius: 14px;
        padding: 28px;
        margin: 12px 0;
    }
    .report-card h3 {
        color: #00B4D8;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .report-card p {
        color: #E0E1DD;
        line-height: 1.7;
    }

    /* ─── Buttons ──────────────────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00B4D8, #2EC4B6) !important;
        color: #0D1B2A !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(0,180,216,0.35) !important;
        transform: translateY(-2px) !important;
    }

    /* ─── Tabs ─────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(13,27,42,0.6);
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #778DA9;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0,180,216,0.15) !important;
        color: #00B4D8 !important;
    }

    /* ─── Dataframe ────────────────────────────────────────────── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ─── Expander ─────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #E0E1DD;
    }

    /* ─── Loading animation ────────────────────────────────────── */
    .typing-indicator {
        display: flex;
        gap: 6px;
        padding: 8px 0;
    }
    .typing-indicator span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00B4D8;
        animation: typingBounce 1.4s infinite ease-in-out;
    }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typingBounce {
        0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* ─── Hide Streamlit branding ──────────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
"""


def metric_card(icon: str, value: str, label: str, variant: str = "") -> str:
    """Generate HTML for a single metric card."""
    cls = f"metric-card {variant}" if variant else "metric-card"
    return f"""
    <div class="{cls}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def agent_badge(agent_type: str, label: str) -> str:
    """Generate an agent badge HTML snippet."""
    return f'<span class="agent-badge {agent_type}">{label}</span>'


def chat_bubble_user(text: str) -> str:
    return f'<div class="chat-user">👤 &nbsp;{text}</div>'



def gradient_divider() -> str:
    return '<div class="gradient-divider"></div>'



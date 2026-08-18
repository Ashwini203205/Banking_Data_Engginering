"""
Banking AI Analytics — Main Streamlit Application
==================================================
Entry point for the Streamlit app. Manages navigation and renders pages.
This is a NEW file that replaces the placeholder app.py.
"""

import sys
import os

# Ensure ai_application is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from styles import get_custom_css

# ─── Page Config (MUST be first Streamlit command) ─────────────────
st.set_page_config(
    page_title="Banking AI Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Inject Custom CSS ────────────────────────────────────────────
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ─── Sidebar Navigation ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0 20px 0;">
        <div style="font-size:2.4rem; margin-bottom:4px;">🏦</div>
        <div style="font-size:1.25rem; font-weight:800; color:#E0E1DD;
                    background: linear-gradient(135deg, #00B4D8, #2EC4B6);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    letter-spacing: 0.5px;">
            Banking AI Analytics
        </div>
        <div style="font-size:0.72rem; color:#778DA9; margin-top:4px;
                    letter-spacing:1.5px; text-transform:uppercase;">
            Data Engineering + AI
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="gradient-divider" style="margin:0 0 16px 0;"></div>
    """, unsafe_allow_html=True)

    # ─── NAVIGATION ──────────────────────────────────────────
    st.markdown("""
    <div class="sidebar-section-title">
        🧭 NAVIGATION
    </div>
    """, unsafe_allow_html=True)

    NAV_OPTIONS = [
        "🏠 Dashboard",
        "🤖 AI Assistant",
        "📊 Data Analytics",
        "🧠 Machine Learning",
        "👥 Customer Segmentation",
        "📄 Reports",
    ]

    # Map alias if needed (e.g. "🏠 Home" -> "🏠 Dashboard")
    if "nav_page" in st.session_state:
        target = st.session_state.pop("nav_page")
        if target == "🏠 Home":
            target = "🏠 Dashboard"
        if target in NAV_OPTIONS:
            st.session_state["nav_selection"] = target

    if "nav_selection" not in st.session_state or st.session_state["nav_selection"] not in NAV_OPTIONS:
        st.session_state["nav_selection"] = NAV_OPTIONS[0]

    page = st.radio(
        "Navigation",
        NAV_OPTIONS,
        key="nav_selection",
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="gradient-divider" style="margin:16px 0 12px 0;"></div>
    """, unsafe_allow_html=True)

    # ─── SYSTEM STATUS ───────────────────────────────────────
    st.markdown("""
    <div class="sidebar-section-title">
        ⚙️ SYSTEM STATUS
    </div>
    """, unsafe_allow_html=True)

    from db import test_connection, get_table_counts
    db_ok = test_connection()
    db_status_text = "Connected" if db_ok else "Disconnected"
    db_badge_class = "connected" if db_ok else "disconnected"

    import os
    env_key = os.getenv("GEMINI_API_KEY", "")
    stored_key = st.session_state.get("gemini_api_key", env_key)
    key_ok = bool(stored_key and stored_key.strip())
    gemini_status_text = "Active" if key_ok else "Missing"
    gemini_badge_class = "active" if key_ok else "missing"

    st.markdown(f"""
    <div class="sidebar-status-item">
        <span>🗄️ PostgreSQL</span>
        <span class="sidebar-status-badge {db_badge_class}">
            ● {db_status_text}
        </span>
    </div>
    <div class="sidebar-status-item">
        <span>🤖 Gemini AI</span>
        <span class="sidebar-status-badge {gemini_badge_class}">
            ● {gemini_status_text}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Gemini Key Input / Configuration
    with st.expander("🔑 Configure Gemini API Key", expanded=not key_ok):
        gemini_key = st.text_input(
            "Gemini API Key Input",
            value=stored_key,
            type="password",
            placeholder="AIzaSy...",
            label_visibility="collapsed",
        )
        if gemini_key != stored_key:
            st.session_state["gemini_api_key"] = gemini_key
            st.rerun()

    # Dynamic Data Layer Summary
    if db_ok:
        with st.expander("📊 Data Layer Counts", expanded=False):
            counts = get_table_counts()
            st.markdown(f"""
            - **Bronze Raw:** {counts.get('bronze.customer_raw', 0):,} rows
            - **Silver Clean:** {counts.get('silver.customer_clean', 0):,} rows
            - **Gold Customer:** {counts.get('gold.customer_summary', 0):,} rows
            - **Gold Education:** {counts.get('gold.education_summary', 0):,} rows
            - **Gold Job:** {counts.get('gold.job_summary', 0):,} rows
            - **Gold Marital:** {counts.get('gold.marital_summary', 0):,} rows
            - **Gold Month:** {counts.get('gold.month_summary', 0):,} rows
            """)

    st.markdown("""
    <div class="gradient-divider" style="margin:16px 0 12px 0;"></div>
    """, unsafe_allow_html=True)

    # ─── TECH STACK ──────────────────────────────────────────
    st.markdown("""
    <div class="sidebar-section-title">
        ⚡ TECH STACK
    </div>
    <div class="tech-stack-container">
        <div class="tech-stack-item"><span>🌪️</span> Apache Airflow</div>
        <div class="tech-stack-item"><span>⚡</span> Apache Spark</div>
        <div class="tech-stack-item"><span>🐘</span> PostgreSQL</div>
        <div class="tech-stack-item"><span>✨</span> Gemini AI</div>
        <div class="tech-stack-item"><span>🔬</span> Scikit-learn</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding-top:16px;">
        <div style="font-size:0.65rem; color:#4a5568;">
            v2.0 · Banking AI Analytics
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Page Routing ─────────────────────────────────────────────────
if page in ("🏠 Dashboard", "🏠 Home"):
    from pages.home import render
    render()

elif page == "🤖 AI Assistant":
    from pages.ai_assistant import render
    render()

elif page == "📊 Data Analytics":
    from pages.data_analytics import render
    render()

elif page == "🧠 Machine Learning":
    from pages.machine_learning import render
    render()

elif page == "👥 Customer Segmentation":
    from pages.customer_segmentation import render
    render()

elif page == "📄 Reports":
    from pages.reports import render
    render()
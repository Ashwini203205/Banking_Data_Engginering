"""
AI Assistant Page — Interactive Banking AI Assistant
====================================================
Natural language interface for banking queries, SQL analysis, ML predictions, and system questions.
Voice input is powered by the browser-native Web Speech API (Chrome/Edge) via a custom HTML component.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from agents.router import route_question
from styles import (
    chat_bubble_user, gradient_divider, agent_badge,
)
from utils import format_rupee, format_number



# Voice Component HTML removed.



# ─── Result Renderers ───────────────────────────────────────────────────────────

def _render_data_result(result: dict):
    """Render data agent results with insight + formatted table in INR."""
    if result.get("insight"):
        st.markdown(result["insight"])

    if isinstance(result.get("data"), pd.DataFrame) and not result["data"].empty:
        df = result["data"].copy()
        for col in df.columns:
            if "balance" in col.lower():
                df[col] = df[col].apply(lambda v: format_rupee(v) if pd.notnull(v) else "₹0")
            elif "customers" in col.lower() or "count" in col.lower():
                df[col] = df[col].apply(lambda v: format_number(v) if pd.notnull(v) else "0")
        st.markdown("")
        st.dataframe(df, use_container_width=True, hide_index=True)


def _render_ml_result(result: dict):
    """Render ML agent results with validation metrics and insights."""
    if result.get("explanation"):
        st.markdown(result["explanation"])

    if result.get("accuracy") is not None:
        st.markdown("##### 📊 Model Validation Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Accuracy",  f"{result['accuracy']:.2%}")
        m2.metric("Precision", f"{result['precision']:.2%}")
        m3.metric("Recall",    f"{result['recall']:.2%}")
        m4.metric("F1 Score",  f"{result['f1']:.2%}")
    if isinstance(result.get("feature_importance"), pd.DataFrame):
        with st.expander("⭐ View Feature Importances", expanded=False):
            st.dataframe(result["feature_importance"], use_container_width=True, hide_index=True)


def _render_support_result(result: dict):
    """Render support agent results."""
    if result.get("answer"):
        st.markdown(result["answer"])
    if result.get("source"):
        st.caption(f"📚 Source: {result['source']}")


# Audio transcription function removed.



def render():
    # ─── Navigation Back Button ────────────────────────────────
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Back to Dashboard", use_container_width=True):
            st.session_state["nav_page"] = "🏠 Dashboard"
            st.rerun()

    # ─── Header ────────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Banking AI Assistant</h1>
        <p>Ask questions in natural language. The AI Router automatically queries PostgreSQL, runs ML predictions, or provides pipeline intelligence.</p>
    </div>
    """, unsafe_allow_html=True)

    # ─── Session state init ─────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ─── Sidebar Controls ──────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-section-title">💬 Chat Controls</div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()




    # ─── Sample Questions (Execute Immediately) ────────────────
    st.markdown("### 💡 Quick Questions (Click to run immediately)")

    samples = [
        ("💰 Average Balance",      "What is the average customer balance?"),
        ("🏦 Total Balance",         "What is the total balance?"),
        ("👥 Customer Statistics",   "Show me customer statistics."),
        ("💼 Job Balances",          "Which job category has the highest balance?"),
        ("💳 Loan Portfolio",        "How many customers have loans?"),
        ("💎 Top 10 Customers",      "Show me the top 10 customers by balance."),
        ("🧠 Predict Subscriptions", "Predict whether a customer is likely to subscribe."),
        ("📈 Model Performance",     "What is the model accuracy?"),
        ("🛟 Data Pipeline",         "How does the pipeline work?"),
    ]

    sample_cols = st.columns(3)
    for i, (label, question_text) in enumerate(samples):
        with sample_cols[i % 3]:
            if st.button(label, key=f"quick_sample_page_{i}", use_container_width=True):
                with st.spinner("🔄 Routing query and querying live data..."):
                    response = route_question(question_text)
                st.session_state.chat_history.append({
                    "question": question_text,
                    "response": response,
                    "source": "button",
                })
                st.rerun()

    st.markdown(gradient_divider(), unsafe_allow_html=True)

    # ─── Render Chronological Conversation Log ─────────────────
    if st.session_state.chat_history:
        st.markdown('<div class="section-title">💬 Chat Conversation</div>', unsafe_allow_html=True)

        for entry in st.session_state.chat_history:
            resp        = entry["response"]
            result      = resp.get("result", {})
            agent_key   = resp.get("agent_key", "support")
            agent_name  = resp.get("agent_name", "Agent")
            agent_icon  = resp.get("agent_icon", "🤖")
            routing_method = resp.get("routing_method", "keyword")
            src         = entry.get("source", "text")
            voice_tag   = " 🎤" if src == "voice" else ""

            # 1. User Message
            st.markdown(
                chat_bubble_user(entry["question"] + voice_tag),
                unsafe_allow_html=True,
            )

            # 2. Agent Response Container
            badge_html = agent_badge(agent_key, f"{agent_icon} {agent_name}")
            route_tag  = "🔑 SQL / Analytics Engine" if routing_method == "keyword" else "✨ Gemini AI Engine"
            st.markdown(
                f"""
                <div class="chat-agent">
                    {badge_html}
                    <span style="float:right; font-size:0.72rem; color:#778DA9;
                                 background:rgba(0,180,216,0.08); padding:3px 10px;
                                 border-radius:8px;">{route_tag}</span>
                    <br><br>
                """,
                unsafe_allow_html=True,
            )

            # 3. Agent Result Content
            if not result.get("success", True) and result.get("error"):
                st.error(f"⚠️ {result['error']}")
            elif agent_key == "data":
                _render_data_result(result)
            elif agent_key == "ml":
                _render_ml_result(result)
            elif agent_key == "support":
                _render_support_result(result)
            else:
                st.info(result.get("message", "Response received."))

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="glass-panel" style="text-align:center; padding:60px;">
            <div style="font-size:3.5rem; margin-bottom:14px;">🤖</div>
            <div style="color:#E0E1DD; font-size:1.25rem; font-weight:700; margin-bottom:4px;">Banking AI Assistant is Ready</div>
            <div style="color:#778DA9; font-size:0.9rem;">
                Select a quick question above or use the chat input below.<br>
                Queries are dynamically answered from real PostgreSQL Gold/Silver layer data and ML models.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── Bottom spacing ──────────────────────────────────────────
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

    # Also support Streamlit floating chat input for convenience
    chat_box_query = st.chat_input("💬 Ask AI Assistant a question…")
    if chat_box_query:
        with st.spinner("🔄 Analyzing question and querying banking data..."):
            response = route_question(chat_box_query)
        st.session_state.chat_history.append({
            "question": chat_box_query,
            "response": response,
            "source":   "text",
        })
        st.rerun()

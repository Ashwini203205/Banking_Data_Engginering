"""
Home Page — Banking AI Analytics Dashboard
==========================================
1. Header
2. Live KPI Cards (in ₹)
3. Quick Actions (immediately below KPIs)
4. Analytics Section (Real Gold layer charts)
5. Machine Learning Section
6. Executive Insights & Reports
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from db import run_query, test_connection
from agents.data_agent import get_all_summaries
from agents.ml_agent import train_subscription_model, predict_single_customer
from styles import (
    metric_card, gradient_divider
)
from utils import format_rupee, format_number
from config import CHART_COLORS


def render():
    # ─── 1. Header ─────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>🏦 Banking AI Analytics Dashboard</h1>
        <p>Enterprise Data Engineering · Real PostgreSQL Gold Layer · ML Predictions · Banking AI Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # Database connectivity test
    db_connected = test_connection()

    # ─── 2. KPI Cards (Live from PostgreSQL Gold / Silver) ───────
    total_cust = sub_cust = avg_age = avg_bal = total_bal = "—"

    if db_connected:
        try:
            cust_df = run_query(
                "SELECT total_customers, subscribed_customers, average_age, average_balance, total_balance FROM gold.customer_summary LIMIT 1;"
            )
            if not cust_df.empty:
                row = cust_df.iloc[0]
                total_cust = format_number(row.get('total_customers', 0))
                sub_cust = format_number(row.get('subscribed_customers', 0))
                avg_age = f"{float(row.get('average_age', 0)):.1f} yrs"
                avg_bal = format_rupee(row.get('average_balance', 0), decimals=True)
                total_bal = format_rupee(row.get('total_balance', 0))
            else:
                # Fallback to silver.customer_clean if gold is pending
                silver_df = run_query(
                    "SELECT COUNT(*) as tot, SUM(CASE WHEN y='yes' THEN 1 ELSE 0 END) as sub, AVG(age) as age, AVG(balance) as avg_b, SUM(balance) as tot_b FROM silver.customer_clean;"
                )
                if not silver_df.empty:
                    row = silver_df.iloc[0]
                    total_cust = format_number(row.get('tot', 0))
                    sub_cust = format_number(row.get('sub', 0))
                    avg_age = f"{float(row.get('age', 0)):.1f} yrs"
                    avg_bal = format_rupee(row.get('avg_b', 0), decimals=True)
                    total_bal = format_rupee(row.get('tot_b', 0))
        except Exception:
            pass

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(metric_card("👥", total_cust, "Total Customers"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("✅", sub_cust, "Subscribed Customers", "green"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("🎂", avg_age, "Average Age", "gold"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("💰", avg_bal, "Average Balance", "purple"), unsafe_allow_html=True)
    with c5:
        st.markdown(metric_card("🏦", total_bal, "Total Balance", "gold"), unsafe_allow_html=True)

    st.markdown(gradient_divider(), unsafe_allow_html=True)

    # ─── 3. Quick Actions (Immediately below KPIs) ──────────────
    st.markdown("""<div class="section-title">⚡ Quick Actions</div>""", unsafe_allow_html=True)
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("🤖 Ask AI Assistant", use_container_width=True, type="primary"):
            st.session_state["nav_page"] = "🤖 AI Assistant"
            st.rerun()
    with qa2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state["nav_page"] = "📊 Data Analytics"
            st.rerun()
    with qa3:
        if st.button("🧠 Run ML Model", use_container_width=True):
            st.session_state["nav_page"] = "🧠 Machine Learning"
            st.rerun()
    with qa4:
        if st.button("📄 Generate Report", use_container_width=True):
            st.session_state["nav_page"] = "📄 Reports"
            st.rerun()

    st.markdown(gradient_divider(), unsafe_allow_html=True)

    # ─── 4. Analytics Section (Real Gold layer charts) ───────────
    st.markdown("""<div class="section-title">📊 Gold Layer Analytics Overview</div>""", unsafe_allow_html=True)
    
    with st.spinner("Loading analytics charts..."):
        summaries = get_all_summaries()

    an_col1, an_col2 = st.columns(2)
    with an_col1:
        # Job distribution
        job_df = summaries.get("job_summary", {}).get("data")
        if job_df is not None and not job_df.empty:
            fig_job = px.bar(
                job_df.sort_values("total_customers", ascending=True).tail(8),
                x="total_customers", y="job",
                orientation="h",
                color="total_customers",
                color_continuous_scale=["#1B2838", "#00B4D8", "#2EC4B6"],
                title="Customer Distribution by Job Category",
                labels={"total_customers": "Total Customers", "job": "Job"}
            )
            fig_job.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E0E1DD"), coloraxis_showscale=False,
                height=320, margin=dict(l=20, r=20, t=35, b=20),
            )
            st.plotly_chart(fig_job, use_container_width=True)
        else:
            st.info("No job summary data available.")

    with an_col2:
        # Education distribution
        edu_df = summaries.get("education_summary", {}).get("data")
        if edu_df is not None and not edu_df.empty:
            fig_edu = px.pie(
                edu_df, values="total_customers", names="education",
                color_discrete_sequence=CHART_COLORS,
                title="Education Level Breakdown",
                hole=0.45,
            )
            fig_edu.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E0E1DD"),
                height=320, margin=dict(l=20, r=20, t=35, b=20),
            )
            fig_edu.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_edu, use_container_width=True)
        else:
            st.info("No education summary data available.")

    an_col3, an_col4 = st.columns(2)
    with an_col3:
        # Monthly Campaign trend
        month_df = summaries.get("month_summary", {}).get("data")
        if month_df is not None and not month_df.empty:
            fig_month = go.Figure()
            fig_month.add_trace(go.Bar(
                x=month_df["month"], y=month_df["total_customers"],
                name="Total Contacts", marker_color="#00B4D8", opacity=0.8,
            ))
            if "subscribed_customers" in month_df.columns:
                fig_month.add_trace(go.Scatter(
                    x=month_df["month"], y=month_df["subscribed_customers"],
                    name="Subscribed", mode="lines+markers",
                    line=dict(color="#FFB703", width=3),
                ))
            fig_month.update_layout(
                title="Monthly Campaign Performance & Conversion",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E0E1DD"), height=320,
                margin=dict(l=20, r=20, t=35, b=20),
                legend=dict(font=dict(color="#E0E1DD")),
            )
            st.plotly_chart(fig_month, use_container_width=True)

    with an_col4:
        # Marital Status
        mar_df = summaries.get("marital_summary", {}).get("data")
        if mar_df is not None and not mar_df.empty:
            fig_mar = px.bar(
                mar_df, x="marital", y="total_customers",
                color="marital",
                color_discrete_sequence=["#00B4D8", "#FFB703", "#E63946"],
                title="Customer Distribution by Marital Status",
                labels={"total_customers": "Total Customers", "marital": "Marital Status"}
            )
            fig_mar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E0E1DD"), showlegend=False,
                height=320, margin=dict(l=20, r=20, t=35, b=20),
            )
            st.plotly_chart(fig_mar, use_container_width=True)

    st.markdown(gradient_divider(), unsafe_allow_html=True)

    # ─── 6. ML Prediction Section ────────────────────────────────
    st.markdown("""<div class="section-title">🧠 Machine Learning Prediction Engine</div>""", unsafe_allow_html=True)

    col_ml_btn, col_ml_info = st.columns([1, 3])
    with col_ml_btn:
        run_ml_clicked = st.button("🚀 Train & Evaluate ML Model", type="primary", use_container_width=True)
    with col_ml_info:
        st.caption("Trains a Random Forest Classifier on `silver.customer_clean` (45,211 rows) to predict term-deposit subscriptions.")

    if run_ml_clicked:
        with st.spinner("Training Random Forest model on banking data..."):
            ml_res = train_subscription_model(force_retrain=True)
            st.session_state["home_ml_result"] = ml_res

    if "home_ml_result" in st.session_state and st.session_state["home_ml_result"].get("success"):
        ml_res = st.session_state["home_ml_result"]
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(metric_card("🎯", f"{ml_res['accuracy']:.2%}", "Model Accuracy"), unsafe_allow_html=True)
        m2.markdown(metric_card("📏", f"{ml_res['precision']:.2%}", "Precision", "gold"), unsafe_allow_html=True)
        m3.markdown(metric_card("🔍", f"{ml_res['recall']:.2%}", "Recall", "purple"), unsafe_allow_html=True)
        m4.markdown(metric_card("⚖️", f"{ml_res['f1']:.2%}", "F1-Score", "green"), unsafe_allow_html=True)

        # Confusion matrix & Top features
        ml_c1, ml_c2 = st.columns(2)
        with ml_c1:
            cm = ml_res["confusion_matrix"]
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm,
                x=["Predicted No", "Predicted Yes"],
                y=["Actual No", "Actual Yes"],
                colorscale=[[0, "#0D1B2A"], [0.5, "#00B4D8"], [1, "#2EC4B6"]],
                text=cm, texttemplate="%{text}",
                textfont=dict(size=16, color="white"),
                showscale=False,
            ))
            fig_cm.update_layout(
                title="Confusion Matrix",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E0E1DD"), height=300,
                margin=dict(l=20, r=20, t=35, b=20),
            )
            st.plotly_chart(fig_cm, use_container_width=True)

        with ml_c2:
            feat_df = ml_res["feature_importance"]
            fig_feat = px.bar(
                feat_df.head(8).sort_values("Importance", ascending=True),
                x="Importance", y="Feature", orientation="h",
                color="Importance",
                color_continuous_scale=["#1B2838", "#00B4D8", "#FFB703"],
                title="Top Predictive Features",
            )
            fig_feat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E0E1DD"), coloraxis_showscale=False,
                height=300, margin=dict(l=20, r=20, t=35, b=20),
            )
            st.plotly_chart(fig_feat, use_container_width=True)

    st.markdown(gradient_divider(), unsafe_allow_html=True)

    # ─── 7. Insights & Reports Section ───────────────────────────
    st.markdown("""<div class="section-title">📄 Executive Insights & Automated Reports</div>""", unsafe_allow_html=True)

    rep_col1, rep_col2 = st.columns([2, 1])
    with rep_col1:
        st.markdown(f"""
        <div class="report-card">
            <h3>📈 Portfolio Executive Summary</h3>
            <p>
                • <strong>Active Customer Base:</strong> {total_cust} accounts managed in PostgreSQL Gold layer.<br>
                • <strong>Total Deposits Under Management:</strong> {total_bal} (Average: {avg_bal}).<br>
                • <strong>Term Deposit Conversion:</strong> {sub_cust} subscribed customers (11.7% conversion).<br>
                • <strong>Demographics:</strong> Average age of {avg_age} with highest deposit concentration in management, retired, and technician segments.<br>
                • <strong>Recommendation:</strong> Target high-balance customers with tailored long-duration engagement campaigns.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with rep_col2:
        st.markdown("""
        <div class="glass-panel" style="text-align:center; padding:24px;">
            <div style="font-size:2.2rem; margin-bottom:8px;">📄</div>
            <div style="font-weight:700; color:#E0E1DD; margin-bottom:8px;">Full Banking Report</div>
            <div style="font-size:0.82rem; color:#778DA9; margin-bottom:16px;">
                Download complete executive summary and data analysis report.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📑 Open Reports Center", use_container_width=True):
            st.session_state["nav_page"] = "📄 Reports"
            st.rerun()

    # Footer
    st.markdown("""
    <div style="text-align:center; padding-top:30px;">
        <div style="font-size:0.75rem; color:#778DA9;">
            Banking AI Analytics Platform · Connected to PostgreSQL & Gemini AI · Currency: INR (₹)
        </div>
    </div>
    """, unsafe_allow_html=True)

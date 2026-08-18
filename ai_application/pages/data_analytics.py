"""
Data Analytics Page — Interactive Charts and In-Depth Insights from the PostgreSQL Gold & Silver Layer.
========================================================================================================
Includes:
- Customer distribution
- Subscription analysis
- Balance distribution
- Age distribution
- Job/category analysis
- Loan/housing analysis
- Campaign/contact analysis
All formatted in Indian Rupee (₹).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from db import run_query, test_connection
from agents.data_agent import get_all_summaries
from styles import metric_card, gradient_divider
from utils import format_rupee, format_number
from config import CHART_COLORS


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
        <h1>📊 Real Banking Data Analytics</h1>
        <p>Interactive exploration of PostgreSQL Gold & Silver layer analytics across demographics, balances, loans, and conversions.</p>
    </div>
    """, unsafe_allow_html=True)

    if not test_connection():
        st.error("❌ Unable to connect to PostgreSQL database. Please ensure the database is running.")
        return

    # ─── Load all Gold data ────────────────────────────────────
    with st.spinner("📡 Querying PostgreSQL database..."):
        summaries = get_all_summaries()
        # Query silver for deep balance and loan analytics
        silver_df = run_query("SELECT age, job, marital, education, balance, housing, loan, duration, campaign, y FROM silver.customer_clean LIMIT 10000;")

    # ─── Customer Summary KPIs ─────────────────────────────────
    cust_data = summaries.get("customer_summary", {}).get("data")
    if cust_data is not None and not cust_data.empty:
        row = cust_data.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(metric_card("👥", format_number(row.get('total_customers', 0)), "Total Customers"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("✅", format_number(row.get('subscribed_customers', 0)), "Subscribed", "green"), unsafe_allow_html=True)
        with c3:
            sub_rate = int(row.get('subscribed_customers', 0)) / max(int(row.get('total_customers', 1)), 1) * 100
            st.markdown(metric_card("📈", f"{sub_rate:.1f}%", "Conversion Rate", "gold"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card("🎂", f"{float(row.get('average_age', 0)):.1f} yrs", "Avg Age", "purple"), unsafe_allow_html=True)
        with c5:
            st.markdown(metric_card("💰", format_rupee(row.get('average_balance', 0), decimals=True), "Avg Balance"), unsafe_allow_html=True)

    st.markdown(gradient_divider(), unsafe_allow_html=True)

    # ─── Tabbed Visualizations ─────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💼 Job & Profession",
        "💰 Balance & Wealth",
        "💳 Loans & Housing",
        "🎯 Subscriptions & Conversion",
        "📚 Education & Demographics",
        "📅 Campaign & Contact",
    ])

    # ─── 1. Job Tab ────────────────────────────────────────────
    with tab1:
        job_data = summaries.get("job_summary", {}).get("data")
        if job_data is not None and not job_data.empty:
            col_chart, col_pie = st.columns(2)

            with col_chart:
                fig = px.bar(
                    job_data.sort_values("total_customers", ascending=True),
                    x="total_customers", y="job",
                    orientation="h",
                    color="total_customers",
                    color_continuous_scale=["#1B2838", "#00B4D8", "#2EC4B6"],
                    title="Customer Distribution by Job Category",
                    labels={"total_customers": "Total Customers", "job": "Job"},
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"), showlegend=False,
                    title_font=dict(size=16, color="#00B4D8"),
                    coloraxis_showscale=False,
                    xaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    yaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    height=450,
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_pie:
                fig2 = px.pie(
                    job_data, values="total_customers", names="job",
                    color_discrete_sequence=CHART_COLORS,
                    title="Job Category Market Share",
                    hole=0.45,
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"),
                    title_font=dict(size=16, color="#00B4D8"),
                    height=450,
                )
                fig2.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig2, use_container_width=True)

            with st.expander("📋 View Raw Job Summary Data"):
                st.dataframe(job_data, use_container_width=True, hide_index=True)
        else:
            st.warning("No job data available in PostgreSQL.")

    # ─── 2. Balance & Wealth Tab ───────────────────────────────
    with tab2:
        if not silver_df.empty:
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                # Balance boxplot by job
                fig_box = px.box(
                    silver_df, x="job", y="balance",
                    color="job",
                    color_discrete_sequence=CHART_COLORS,
                    title="Balance Distribution Across Professions (₹)",
                    labels={"balance": "Account Balance (₹)", "job": "Job Category"},
                )
                fig_box.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"), showlegend=False,
                    title_font=dict(size=16, color="#00B4D8"),
                    xaxis=dict(gridcolor="rgba(0,180,216,0.08)", tickangle=-45),
                    yaxis=dict(gridcolor="rgba(0,180,216,0.08)", range=[-2000, 25000]),
                    height=450,
                )
                st.plotly_chart(fig_box, use_container_width=True)

            with b_col2:
                # Average balance by education and marital
                avg_seg = silver_df.groupby(["education", "marital"])["balance"].mean().reset_index()
                fig_bar = px.bar(
                    avg_seg, x="education", y="balance", color="marital",
                    barmode="group",
                    color_discrete_sequence=["#00B4D8", "#FFB703", "#E63946"],
                    title="Average Account Balance by Segment (₹)",
                    labels={"balance": "Average Balance (₹)", "education": "Education Level", "marital": "Marital Status"},
                )
                fig_bar.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"),
                    title_font=dict(size=16, color="#00B4D8"),
                    xaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    yaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    height=450,
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No silver layer balance records loaded.")

    # ─── 3. Loans & Housing Tab ────────────────────────────────
    with tab3:
        if not silver_df.empty:
            l_col1, l_col2 = st.columns(2)
            with l_col1:
                # Housing vs Personal loan cross-tab
                loan_counts = silver_df.groupby(["housing", "loan"]).size().reset_index(name="count")
                fig_loan = px.bar(
                    loan_counts, x="housing", y="count", color="loan",
                    barmode="group",
                    color_discrete_sequence=["#00B4D8", "#E63946"],
                    title="Housing vs Personal Loan Distribution",
                    labels={"housing": "Has Housing Loan", "loan": "Has Personal Loan", "count": "Customer Count"},
                )
                fig_loan.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"),
                    title_font=dict(size=16, color="#00B4D8"),
                    xaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    yaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    height=420,
                )
                st.plotly_chart(fig_loan, use_container_width=True)

            with l_col2:
                # Loan impact on balance
                loan_bal = silver_df.groupby(["housing", "loan"])["balance"].mean().reset_index()
                loan_bal["Loan Profile"] = "Housing: " + loan_bal["housing"] + " | Personal: " + loan_bal["loan"]
                fig_lbal = px.bar(
                    loan_bal, x="Loan Profile", y="balance",
                    color="balance",
                    color_continuous_scale=["#1B2838", "#2EC4B6", "#FFB703"],
                    title="Average Account Balance by Loan Status (₹)",
                    labels={"balance": "Average Balance (₹)"},
                )
                fig_lbal.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"), coloraxis_showscale=False,
                    title_font=dict(size=16, color="#00B4D8"),
                    xaxis=dict(gridcolor="rgba(0,180,216,0.08)", tickangle=-20),
                    yaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    height=420,
                )
                st.plotly_chart(fig_lbal, use_container_width=True)

    # ─── 4. Subscriptions Tab ──────────────────────────────────
    with tab4:
        if not silver_df.empty:
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                # Subscription by Job
                job_sub = silver_df.groupby("job")["y"].apply(lambda s: (s == "yes").mean() * 100).reset_index(name="Conversion Rate %")
                fig_jsub = px.bar(
                    job_sub.sort_values("Conversion Rate %", ascending=True),
                    x="Conversion Rate %", y="job",
                    orientation="h",
                    color="Conversion Rate %",
                    color_continuous_scale=["#1B2838", "#06D6A0", "#2EC4B6"],
                    title="Term Deposit Subscription Rate by Job (%)",
                )
                fig_jsub.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"), coloraxis_showscale=False,
                    title_font=dict(size=16, color="#00B4D8"),
                    xaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    yaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                    height=420,
                )
                st.plotly_chart(fig_jsub, use_container_width=True)

            with sub_col2:
                # Overall Subscription Pie
                dep_summary = summaries.get("deposit_summary", {}).get("data")
                if dep_summary is None or dep_summary.empty:
                    dep_summary = silver_df["y"].value_counts().reset_index()
                    dep_summary.columns = ["subscribed", "total_customers"]
                fig_sub_pie = px.pie(
                    dep_summary, values="total_customers", names="subscribed",
                    color="subscribed",
                    color_discrete_map={"yes": "#06D6A0", "no": "#E63946"},
                    title="Overall Portfolio Subscription Share",
                    hole=0.5,
                )
                fig_sub_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E0E1DD"),
                    title_font=dict(size=16, color="#00B4D8"),
                    height=420,
                )
                fig_sub_pie.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_sub_pie, use_container_width=True)

    # ─── 5. Education & Demographics Tab ───────────────────────
    with tab5:
        edu_data = summaries.get("education_summary", {}).get("data")
        mar_data = summaries.get("marital_summary", {}).get("data")
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            if edu_data is not None and not edu_data.empty:
                fig_e = px.bar(
                    edu_data, x="education", y="total_customers",
                    color="education", color_discrete_sequence=CHART_COLORS,
                    title="Education Level Distribution",
                    labels={"total_customers": "Customers", "education": "Education"},
                )
                fig_e.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"), showlegend=False,
                    title_font=dict(size=16, color="#00B4D8"),
                    height=400,
                )
                st.plotly_chart(fig_e, use_container_width=True)

        with e_col2:
            if mar_data is not None and not mar_data.empty:
                fig_m = px.pie(
                    mar_data, values="total_customers", names="marital",
                    color_discrete_sequence=["#00B4D8", "#FFB703", "#E63946"],
                    title="Marital Status Distribution",
                    hole=0.45,
                )
                fig_m.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E0E1DD"),
                    title_font=dict(size=16, color="#00B4D8"),
                    height=400,
                )
                fig_m.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_m, use_container_width=True)

    # ─── 6. Campaign & Monthly Tab ─────────────────────────────
    with tab6:
        month_data = summaries.get("month_summary", {}).get("data")
        if month_data is not None and not month_data.empty:
            fig_mo = go.Figure()
            fig_mo.add_trace(go.Bar(
                x=month_data["month"], y=month_data["total_customers"],
                name="Total Contacts", marker_color="#00B4D8", opacity=0.8,
            ))
            if "subscribed_customers" in month_data.columns:
                fig_mo.add_trace(go.Scatter(
                    x=month_data["month"], y=month_data["subscribed_customers"],
                    name="Subscribed Customers", mode="lines+markers",
                    line=dict(color="#FFB703", width=3),
                    marker=dict(size=8),
                ))
            fig_mo.update_layout(
                title="Monthly Campaign Contacts vs Term Deposit Conversions",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E0E1DD"),
                title_font=dict(size=16, color="#00B4D8"),
                legend=dict(font=dict(color="#E0E1DD")),
                xaxis=dict(gridcolor="rgba(0,180,216,0.08)", title="Month"),
                yaxis=dict(gridcolor="rgba(0,180,216,0.08)", title="Count"),
                height=450,
            )
            st.plotly_chart(fig_mo, use_container_width=True)
            with st.expander("📋 View Monthly Table"):
                st.dataframe(month_data, use_container_width=True, hide_index=True)

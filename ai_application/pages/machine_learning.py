"""
Machine Learning Page — Train Model, View Real Metrics, Make Single Customer Predictions.
========================================================================================
Uses Random Forest on silver.customer_clean. All monetary values in Indian Rupees (₹).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from agents.ml_agent import (
    train_subscription_model, predict_single_customer, explain_ml_results,
)
from styles import metric_card, gradient_divider


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
        <h1>🧠 Machine Learning Intelligence</h1>
        <p>Enterprise Subscription Prediction Model — Train, evaluate, and perform real-time customer inference with Random Forest</p>
    </div>
    """, unsafe_allow_html=True)

    # ─── Train Model Section ───────────────────────────────────
    st.markdown('<div class="section-title">🔧 Model Execution & Training</div>', unsafe_allow_html=True)

    if st.button("🚀 Train & Evaluate Random Forest Model", type="primary", use_container_width=True):
        with st.spinner("🔄 Training Random Forest classifier on silver.customer_clean..."):
            result = train_subscription_model(force_retrain=True)
            st.session_state["ml_result"] = result

    # ─── Auto-load cached model if available ───────────────────
    if "ml_result" not in st.session_state:
        # Pre-train silently or check cache
        cached = train_subscription_model(force_retrain=False)
        if cached.get("success"):
            st.session_state["ml_result"] = cached

    # ─── Display Results ───────────────────────────────────────
    if "ml_result" in st.session_state:
        result = st.session_state["ml_result"]

        if not result.get("success"):
            st.error(f"❌ {result.get('error', 'Model training failed.')}")
            return

        st.success("✅ Model active and trained on real PostgreSQL data!")

        st.markdown(gradient_divider(), unsafe_allow_html=True)

        # ─── Metrics ───────────────────────────────────────────
        st.markdown('<div class="section-title">📈 Model Performance Metrics</div>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(metric_card("🎯", f"{result['accuracy']:.2%}", "Accuracy"), unsafe_allow_html=True)
        with m2:
            st.markdown(metric_card("📏", f"{result['precision']:.2%}", "Precision", "gold"), unsafe_allow_html=True)
        with m3:
            st.markdown(metric_card("🔍", f"{result['recall']:.2%}", "Recall", "purple"), unsafe_allow_html=True)
        with m4:
            st.markdown(metric_card("⚖️", f"{result['f1']:.2%}", "F1 Score", "green"), unsafe_allow_html=True)

        info1, info2 = st.columns(2)
        with info1:
            st.info(f"🏋️ Training samples: **{result['train_size']:,} records**")
        with info2:
            st.info(f"🧪 Test evaluation samples: **{result['test_size']:,} records**")

        st.markdown(gradient_divider(), unsafe_allow_html=True)

        # ─── Charts ────────────────────────────────────────────
        chart1, chart2 = st.columns(2)

        # Confusion Matrix
        with chart1:
            st.markdown('<div class="section-title">🔢 Confusion Matrix</div>', unsafe_allow_html=True)
            cm = result["confusion_matrix"]
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm,
                x=["Predicted No", "Predicted Yes"],
                y=["Actual No", "Actual Yes"],
                colorscale=[[0, "#0D1B2A"], [0.5, "#00B4D8"], [1, "#2EC4B6"]],
                text=cm,
                texttemplate="%{text}",
                textfont=dict(size=18, color="white"),
                showscale=False,
            ))
            fig_cm.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E0E1DD"),
                height=350,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(side="bottom"),
            )
            st.plotly_chart(fig_cm, use_container_width=True)

        # Feature Importance
        with chart2:
            st.markdown('<div class="section-title">⭐ Feature Importance (Top 12)</div>', unsafe_allow_html=True)
            feat_df = result["feature_importance"].head(12)
            fig_feat = px.bar(
                feat_df.sort_values("Importance", ascending=True),
                x="Importance", y="Feature",
                orientation="h",
                color="Importance",
                color_continuous_scale=["#1B2838", "#00B4D8", "#FFB703"],
            )
            fig_feat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E0E1DD"),
                coloraxis_showscale=False,
                height=350,
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
                yaxis=dict(gridcolor="rgba(0,180,216,0.08)"),
            )
            st.plotly_chart(fig_feat, use_container_width=True)

        # ─── AI Explanation ────────────────────────────────────
        st.markdown(gradient_divider(), unsafe_allow_html=True)
        st.markdown('<div class="section-title">💡 Data Scientist Insights & Interpretation</div>', unsafe_allow_html=True)

        if "ml_explanation" not in st.session_state:
            with st.spinner("🤖 Generating model interpretation..."):
                explanation = explain_ml_results(result, "Explain the model performance and key drivers")
                st.session_state["ml_explanation"] = explanation

        st.markdown(f"""
        <div class="glass-panel">
            {st.session_state.get("ml_explanation", "No explanation available.")}
        </div>
        """, unsafe_allow_html=True)

        # ─── Prediction Form ──────────────────────────────────
        st.markdown(gradient_divider(), unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔮 Real-Time Customer Subscription Predictor</div>', unsafe_allow_html=True)

        with st.form("prediction_form"):
            pf1, pf2, pf3, pf4 = st.columns(4)

            with pf1:
                age = st.number_input("Customer Age", min_value=18, max_value=100, value=35)
                job = st.selectbox("Job Category", [
                    "management", "technician", "entrepreneur", "blue-collar",
                    "admin.", "services", "retired", "self-employed",
                    "housemaid", "student", "unemployed", "unknown",
                ])

            with pf2:
                marital = st.selectbox("Marital Status", ["married", "single", "divorced"])
                education = st.selectbox("Education Level", ["primary", "secondary", "tertiary", "unknown"])

            with pf3:
                balance = st.number_input("Account Balance (₹)", min_value=-50000, max_value=5000000, value=25000, step=1000)
                housing = st.selectbox("Housing Loan", ["no", "yes"])

            with pf4:
                loan = st.selectbox("Personal Loan", ["no", "yes"])
                duration = st.number_input("Call Duration (seconds)", min_value=0, max_value=5000, value=300, step=30)

            pf5, pf6, pf7 = st.columns(3)
            with pf5:
                campaign = st.number_input("Contacts during Campaign", min_value=1, max_value=50, value=1)
            with pf6:
                pdays = st.number_input("Days Since Previous Contact (-1 = never)", min_value=-1, max_value=999, value=-1)
            with pf7:
                previous = st.number_input("Previous Contacts Count", min_value=0, max_value=50, value=0)

            poutcome = st.selectbox("Previous Campaign Outcome", ["unknown", "success", "failure", "other"])

            submitted = st.form_submit_button("🔮 Predict Customer Subscription Likelihood", type="primary", use_container_width=True)

        if submitted:
            customer = {
                "age": age, "job": job, "marital": marital, "education": education,
                "balance": balance, "housing": housing, "loan": loan,
                "duration": duration, "campaign": campaign, "pdays": pdays,
                "previous": previous, "poutcome": poutcome,
            }
            pred_result = predict_single_customer(result["pipeline"], customer)

            if pred_result["success"]:
                pred_col1, pred_col2, pred_col3 = st.columns(3)
                with pred_col1:
                    st.markdown(metric_card(
                        "🔮",
                        pred_result["label"],
                        "Prediction Outcome",
                        "green" if pred_result["prediction"] == 1 else "purple",
                    ), unsafe_allow_html=True)
                with pred_col2:
                    st.markdown(metric_card(
                        "✅", f"{pred_result['probability_yes']:.1%}", "Subscription Probability", "green"
                    ), unsafe_allow_html=True)
                with pred_col3:
                    st.markdown(metric_card(
                        "❌", f"{pred_result['probability_no']:.1%}", "Decline Probability"
                    ), unsafe_allow_html=True)

                # Gauge chart
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=pred_result["probability_yes"] * 100,
                    title={"text": "Subscription Propensity Score", "font": {"color": "#E0E1DD", "size": 16}},
                    number={"suffix": "%", "font": {"color": "#00B4D8", "size": 36}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#778DA9"},
                        "bar": {"color": "#00B4D8"},
                        "bgcolor": "#1B2838",
                        "bordercolor": "rgba(0,180,216,0.2)",
                        "steps": [
                            {"range": [0, 30], "color": "rgba(230,57,70,0.2)"},
                            {"range": [30, 70], "color": "rgba(255,183,3,0.2)"},
                            {"range": [70, 100], "color": "rgba(6,214,160,0.2)"},
                        ],
                        "threshold": {
                            "line": {"color": "#FFB703", "width": 3},
                            "thickness": 0.8,
                            "value": 50,
                        },
                    },
                ))
                fig_gauge.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E0E1DD"),
                    height=280,
                    margin=dict(l=30, r=30, t=40, b=20),
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
            else:
                st.error(f"Prediction failed: {pred_result.get('error')}")

    else:
        st.markdown("""
        <div class="glass-panel" style="text-align:center; padding:60px;">
            <div style="font-size:3.5rem; margin-bottom:14px;">🧠</div>
            <div style="color:#778DA9; font-size:1.1rem;">
                Click the button above to train the subscription prediction model<br>
                <span style="font-size:0.85rem;">Uses Random Forest on data from <code>silver.customer_clean</code></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
